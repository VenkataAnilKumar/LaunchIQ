"""Launch service business logic."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository
from src.packages.config.models import PIPELINE_SEQUENCE

if TYPE_CHECKING:
	from src.apps.api.models.launch import Launch


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

	async def get(self, launch_id: str) -> dict[str, Any] | None:
		async with AsyncSessionLocal() as db:
			launch_repo = LaunchRepository(db)
			agent_repo = AgentRepository(db)

			launch = await launch_repo.get(launch_id)
			if launch is None:
				return None

			pipeline = await agent_repo.get_by_launch(launch_id)
			return {
				"launch_id": launch.launch_id,
				"status": _status_value(launch.status),
				"brief": launch.brief_output or {},
				"pipeline": [
					{
						"agent_id": run.agent_id,
						"status": run.status,
						"output": run.output,
						"tokens_used": run.tokens_used,
						"started_at": run.started_at.isoformat() if run.started_at else None,
						"completed_at": run.completed_at.isoformat() if run.completed_at else None,
						"error": run.error,
					}
					for run in pipeline
				],
				"hitl_pending": _status_value(launch.status) == "hitl_pending",
				"hitl_checkpoint": None,
			}

	async def run_pipeline(self, launch_id: str) -> None:
		from src.apps.api.workers.tasks import run_orchestrator_task

		run_orchestrator_task.delay(launch_id)


def get_launch_service() -> LaunchService:
	return LaunchService()

