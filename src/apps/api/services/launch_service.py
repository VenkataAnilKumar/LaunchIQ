"""Launch service business logic."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from src.agents.orchestrator.synthesizer import build_brief
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.hitl_repo import HITLRepository
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository
from src.packages.config.models import PIPELINE_SEQUENCE

if TYPE_CHECKING:
	from src.apps.api.models.launch import Launch

logger = logging.getLogger(__name__)


def _status_value(status: Any) -> str:
	return status.value if hasattr(status, "value") else str(status)


class LaunchService:
	async def create(self, data: dict[str, Any], user_id: str = "dev") -> dict[str, Any]:
		async with AsyncSessionLocal() as db:
			launch_repo = LaunchRepository(db)
			agent_repo = AgentRepository(db)

			launch = await launch_repo.create(user_id=user_id, data=data)
			for agent_id in PIPELINE_SEQUENCE:
				await agent_repo.create(launch_id=launch.launch_id, agent_id=agent_id)

			created_at = launch.created_at or datetime.utcnow()
			return {
				"launch_id": launch.launch_id,
				"status": _status_value(launch.status),
				"created_at": created_at.isoformat(),
			}

	async def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
		async with AsyncSessionLocal() as db:
			launch_repo = LaunchRepository(db)
			launches = await launch_repo.list_by_user(user_id)
			return [
				{
					"launch_id": launch.launch_id,
					"status": _status_value(launch.status),
					"product_name": launch.product_name,
					"description": launch.description,
					"target_market": launch.target_market,
					"competitors": list(launch.competitors or []),
					"launch_date": launch.launch_date,
					"created_at": launch.created_at.isoformat() if launch.created_at else datetime.utcnow().isoformat(),
					"updated_at": launch.updated_at.isoformat() if launch.updated_at else datetime.utcnow().isoformat(),
				}
				for launch in launches
			]

	async def owns(self, launch_id: str, user_id: str) -> bool:
		async with AsyncSessionLocal() as db:
			launch = await LaunchRepository(db).get(launch_id)
			return launch is not None and launch.user_id == user_id

	async def get(self, launch_id: str, user_id: str | None = None) -> dict[str, Any] | None:
		"""Launch detail. When user_id is given, launches owned by others read as missing."""
		async with AsyncSessionLocal() as db:
			launch_repo = LaunchRepository(db)
			agent_repo = AgentRepository(db)

			launch = await launch_repo.get(launch_id)
			if launch is None or (user_id is not None and launch.user_id != user_id):
				return None

			runs = await agent_repo.get_by_launch(launch_id)
			pending = await HITLRepository(db).get_pending(launch_id)
			order = {a: i for i, a in enumerate(PIPELINE_SEQUENCE)}
			runs = sorted(runs, key=lambda r: order.get(r.agent_id, 99))
			outputs = {r.agent_id: r.output for r in runs if r.status == "completed" and r.output}
			final = launch.brief_output or {}
			return {
				"launch_id": launch.launch_id,
				"status": _status_value(launch.status),
				"input": {
					"product_name": launch.product_name,
					"description": launch.description,
					"target_market": launch.target_market,
					"competitors": list(launch.competitors or []),
					"launch_date": launch.launch_date,
				},
				# Sections are assembled live so pages can render as soon as an agent finishes.
				"brief": build_brief(outputs),
				"pipeline": [
					{
						"agent_id": run.agent_id,
						"status": run.status,
						"output": run.output,
						"tokens_used": run.tokens_used,
						"cost_usd": run.cost_usd or 0.0,
						"started_at": run.started_at.isoformat() if run.started_at else None,
						"completed_at": run.completed_at.isoformat() if run.completed_at else None,
						"error": run.error,
					}
					for run in runs
				],
				"hitl_pending": pending is not None,
				"hitl_checkpoint": pending.checkpoint if pending else None,
				"total_cost_usd": round(sum(r.cost_usd or 0.0 for r in runs), 6),
				"export_ready": bool(final.get("markdown")),
			}

	async def get_export(self, launch_id: str, user_id: str) -> dict[str, Any] | None:
		"""Final synthesized launch brief (with Markdown), or None if not owned / not finished."""
		async with AsyncSessionLocal() as db:
			launch = await LaunchRepository(db).get(launch_id)
			if launch is None or launch.user_id != user_id or not launch.brief_output:
				return None
			return {"product_name": launch.product_name, **launch.brief_output}

	async def run_pipeline(self, launch_id: str) -> None:
		"""Hand the launch to the worker; a launch that cannot be queued is marked failed."""
		from src.apps.api.workers.runner import enqueue_orchestrator

		try:
			enqueue_orchestrator(launch_id)
		except Exception:
			logger.exception("Could not enqueue launch %s", launch_id)
			async with AsyncSessionLocal() as db:
				await LaunchRepository(db).update_status(launch_id, "failed")


def get_launch_service() -> LaunchService:
	return LaunchService()

