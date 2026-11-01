"""Orchestrator agent implementation.

Event-driven and resumable: a run executes agents until it reaches a human
checkpoint (HITL) and then *returns* with status ``hitl_pending``. When a human
decides, the API enqueues a new run; completed agents are skipped (their
outputs are loaded from the RunStore) and the pipeline continues from there.
No worker slot is held while waiting for a human.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent
from src.agents._base.llm import BudgetExceededError
from src.apps.api.config import get_settings
from src.memory.short_term.session_store import SessionStore

from .dispatcher import AgentDispatcher
from .run_store import DbRunStore, RunStore
from .schemas import OrchestratorOutput
from .synthesizer import synthesize

logger = logging.getLogger(__name__)

MAX_AGENT_ATTEMPTS = 2


def _utc_iso_timestamp() -> str:
	return datetime.now(UTC).isoformat()


def _load_system_prompt() -> str:
	prompt_path = Path(__file__).parent / "prompts" / "system.md"
	if not prompt_path.exists():
		return "You are the LaunchIQ orchestrator."
	return prompt_path.read_text(encoding="utf-8")


class OrchestratorAgent(BaseAgent):
	PIPELINE_SEQUENCE = [
		"market_intelligence",
		"audience_insight",
		"launch_strategy",
		"content_generation",
	]
	HITL_AFTER = {
		"market_intelligence": "brief_review",
		"launch_strategy": "strategy_review",
	}

	def __init__(
		self,
		store: RunStore | None = None,
		dispatcher: AgentDispatcher | None = None,
		session_store: SessionStore | None = None,
	) -> None:
		config = AgentConfig(
			agent_id="orchestrator",
			model="opus",
			enable_thinking=True,
			thinking_budget=8000,
			system_prompt=_load_system_prompt(),
		)
		super().__init__(config)
		self.store: RunStore = store or DbRunStore()
		self.dispatcher = dispatcher or AgentDispatcher()
		self._session_store = session_store
		self._attempts = MAX_AGENT_ATTEMPTS

	def get_output_schema(self) -> type[BaseModel]:
		return OrchestratorOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		launch_id = str(payload.get("launch_id", ""))
		if not launch_id:
			raise ValueError("Orchestrator payload must include launch_id")

		states = await self.store.get_agent_states(launch_id)
		outputs: dict[str, Any] = {
			agent_id: st["output"]
			for agent_id, st in states.items()
			if st.get("status") == "completed" and st.get("output") is not None
		}
		spent = sum(float(st.get("cost_usd") or 0.0) for st in states.values())
		budget = get_settings().launch_cost_budget_usd

		await self.store.set_launch_status(launch_id, "running")

		for agent_id in self.PIPELINE_SEQUENCE:
			if agent_id not in outputs:
				if budget and spent >= budget:
					return await self._finish(
						launch_id, "failed", outputs, spent,
						reason=f"cost budget exceeded (${spent:.2f} >= ${budget:.2f})",
					)
				try:
					result = await self._run_agent(launch_id, agent_id, payload, outputs)
				except Exception as exc:
					return await self._finish(launch_id, "failed", outputs, spent, reason=str(exc), agent_id=agent_id)
				outputs[agent_id] = result.output
				spent += result.cost_usd

			checkpoint = self.HITL_AFTER.get(agent_id)
			if not checkpoint:
				continue

			record = await self.store.get_checkpoint(launch_id, checkpoint)
			if record is None:
				await self._open_checkpoint(launch_id, checkpoint, agent_id, outputs[agent_id])
				return await self._finish(launch_id, "hitl_pending", outputs, spent, checkpoint=checkpoint)
			decision = record.get("decision")
			if decision is None:
				return await self._finish(launch_id, "hitl_pending", outputs, spent, checkpoint=checkpoint)
			if decision == "reject":
				return await self._finish(
					launch_id, "rejected", outputs, spent, reason="Rejected during human review", checkpoint=checkpoint
				)

		final = synthesize(payload, outputs, {"cost_usd": round(spent, 6)})
		await self.store.save_final_output(launch_id, final)
		return await self._finish(launch_id, "completed", outputs, spent)

	# ------------------------------------------------------------------ #

	async def _run_agent(
		self,
		launch_id: str,
		agent_id: str,
		payload: dict[str, Any],
		outputs: dict[str, Any],
	) -> AgentResult:
		await self.store.mark_started(launch_id, agent_id)
		await self._publish_event(launch_id, {"type": "agent_started", "launch_id": launch_id, "agent_id": agent_id})

		agent_payload = {**payload, "launch_id": launch_id, "prior_outputs": dict(outputs)}
		last_error: Exception | None = None
		for attempt in range(1, self._attempts + 1):
			try:
				result = await self.dispatcher.dispatch_result(agent_id, agent_payload)
				await self.store.mark_completed(
					launch_id,
					agent_id,
					result.output,
					{"tokens_used": result.tokens_used, "cost_usd": result.cost_usd},
				)
				await self._publish_event(
					launch_id,
					{
						"type": "agent_completed",
						"launch_id": launch_id,
						"agent_id": agent_id,
						"output": result.output,
						"tokens_used": result.tokens_used,
						"cost_usd": result.cost_usd,
					},
				)
				return result
			except Exception as exc:  # noqa: PERF203
				last_error = exc
				logger.warning("Agent %s attempt %d/%d failed: %s", agent_id, attempt, self._attempts, exc)

		error = str(last_error) if last_error else "unknown_error"
		await self.store.mark_failed(launch_id, agent_id, error)
		await self._publish_event(
			launch_id, {"type": "agent_failed", "launch_id": launch_id, "agent_id": agent_id, "error": error}
		)
		raise RuntimeError(f"{agent_id} failed: {error}")

	async def _open_checkpoint(self, launch_id: str, checkpoint: str, agent_id: str, output: dict[str, Any]) -> None:
		record = await self.store.create_checkpoint(launch_id, checkpoint, agent_id, output)
		await self._publish_event(
			launch_id,
			{
				"type": "hitl_required",
				"launch_id": launch_id,
				"checkpoint": checkpoint,
				"agent_id": agent_id,
				"output_preview": output,
				"created_at": record.get("created_at") or _utc_iso_timestamp(),
			},
		)

	async def _finish(
		self,
		launch_id: str,
		status: str,
		outputs: dict[str, Any],
		spent: float,
		reason: str | None = None,
		checkpoint: str | None = None,
		agent_id: str | None = None,
	) -> AgentResult:
		await self.store.set_launch_status(launch_id, status)
		event_type = {"completed": "launch_completed", "failed": "launch_failed", "rejected": "launch_rejected"}.get(status)
		if event_type:
			await self._publish_event(
				launch_id,
				{"type": event_type, "launch_id": launch_id, "status": status, "reason": reason, "agent_id": agent_id},
			)
		model = OrchestratorOutput(
			launch_id=launch_id,
			status=status,  # type: ignore[arg-type]
			agent_outputs=outputs,
			hitl_checkpoint=checkpoint if status == "hitl_pending" else None,
			failure_reason=reason,
			cost_usd=round(spent, 6),
		)
		return AgentResult(
			agent_id=self.config.agent_id,
			output=model.model_dump(),
			hitl_required=status == "hitl_pending",
			hitl_checkpoint=model.hitl_checkpoint,
			cost_usd=round(spent, 6),
		)

	async def _publish_event(self, launch_id: str, event: dict[str, Any]) -> None:
		# Event streaming must never block or fail the workflow.
		event = {**event, "timestamp": _utc_iso_timestamp()}
		try:
			store = self._session_store or SessionStore()
			await store.publish(f"launch:{launch_id}:events", event)
		except Exception:
			logger.warning("Failed to publish event", extra={"launch_id": launch_id, "event_type": event.get("type")})

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)
