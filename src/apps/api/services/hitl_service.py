"""HITL service: records human decisions durably and resumes the pipeline."""
from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from src.agents.audience_insight.schemas import AudienceInsightOutput
from src.agents.content_generation.schemas import ContentBundle
from src.agents.launch_strategy.schemas import LaunchStrategyOutput
from src.agents.market_intelligence.schemas import MarketIntelligenceOutput
from src.memory.short_term.session_store import SessionStore
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.hitl_repo import HITLRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository

logger = logging.getLogger(__name__)

AGENT_OUTPUT_SCHEMAS: dict[str, type[BaseModel]] = {
	"market_intelligence": MarketIntelligenceOutput,
	"audience_insight": AudienceInsightOutput,
	"launch_strategy": LaunchStrategyOutput,
	"content_generation": ContentBundle,
}


class InvalidEditsError(ValueError):
	"""Edits do not produce a schema-valid agent output."""


class CheckpointMismatchError(RuntimeError):
	"""The decision targets a different checkpoint than the one now awaiting review."""

	def __init__(self, expected: str, pending: str) -> None:
		super().__init__(f"Decision was for '{expected}' but '{pending}' is now awaiting review")
		self.pending = pending


class HITLService:
	async def get_pending(self, launch_id: str) -> dict[str, Any] | None:
		async with AsyncSessionLocal() as db:
			rec = await HITLRepository(db).get_pending(launch_id)
		if rec is None:
			return None
		return {
			"launch_id": rec.launch_id,
			"checkpoint": rec.checkpoint,
			"agent_id": rec.agent_id,
			"output_preview": rec.output_preview,
			"created_at": rec.created_at.isoformat() if rec.created_at else "",
		}

	async def resolve(
		self,
		launch_id: str,
		decision: str,
		edits: dict[str, Any] | None,
		comment: str | None,
		checkpoint: str | None = None,
	) -> dict[str, Any] | None:
		"""Apply a decision. Returns None when nothing is awaiting review.

		``checkpoint`` guards against stale clients: a late click on an old review must not
		approve the next one blind.
		"""
		async with AsyncSessionLocal() as db:
			hitl = HITLRepository(db)
			pending = await hitl.get_pending(launch_id)
			if pending is None:
				return None

			if checkpoint and checkpoint != pending.checkpoint:
				raise CheckpointMismatchError(checkpoint, pending.checkpoint)

			if decision == "edit" and not edits:
				raise InvalidEditsError("decision 'edit' requires a non-empty edits object")

			if edits:
				await self._apply_edits(db, launch_id, pending.agent_id, edits)

			# The conditional update makes concurrent/double submissions resolve only once.
			if not await hitl.resolve_record(pending.id, decision, edits, comment):
				return None

			launches = LaunchRepository(db)
			if decision == "reject":
				await launches.update_status(launch_id, "rejected")
			else:
				await launches.update_status(launch_id, "running")

		session = SessionStore()
		event = {
			"type": "hitl_resolved",
			"launch_id": launch_id,
			"checkpoint": pending.checkpoint,
			"decision": decision,
			"comment": comment,
		}
		try:
			await session.publish(f"launch:{launch_id}:events", event)
		except Exception:  # noqa: BLE001 - best-effort event publish
			# Streaming is best-effort; the decision is already durable.
			logger.warning("Could not publish hitl_resolved for %s", launch_id)

		if decision == "reject":
			return {"next_step": "halted"}

		from src.apps.api.workers.runner import enqueue_orchestrator

		enqueue_orchestrator(launch_id)
		return {"next_step": "resume_pipeline"}

	async def _apply_edits(self, db, launch_id: str, agent_id: str, edits: dict[str, Any]) -> None:
		repo = AgentRepository(db)
		runs = {r.agent_id: r for r in await repo.get_by_launch(launch_id)}
		run = runs.get(agent_id)
		if run is None or not isinstance(run.output, dict):
			raise InvalidEditsError(f"No output to edit for {agent_id}")
		merged = {**run.output, **edits}
		schema = AGENT_OUTPUT_SCHEMAS.get(agent_id)
		if schema is not None:
			try:
				merged = schema(**merged).model_dump()
			except ValidationError as exc:
				raise InvalidEditsError(f"Edits make {agent_id} output invalid: {exc.errors()[:3]}") from exc
		await repo.update_output(launch_id, agent_id, merged)


def get_hitl_service() -> HITLService:
	return HITLService()
