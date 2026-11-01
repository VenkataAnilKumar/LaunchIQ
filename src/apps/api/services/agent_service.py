"""Agent service business logic."""
from __future__ import annotations

from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository


class AgentService:
	async def get_pipeline_status(self, launch_id: str) -> list[dict] | None:
		async with AsyncSessionLocal() as db:
			repo = AgentRepository(db)
			runs = await repo.get_by_launch(launch_id)
			if not runs:
				return None
			return [
				{
					"agent_id": run.agent_id,
					"status": run.status,
					"output": run.output,
					"tokens_used": run.tokens_used,
					"started_at": run.started_at.isoformat() if run.started_at else None,
					"completed_at": run.completed_at.isoformat() if run.completed_at else None,
					"error": run.error,
				}
				for run in runs
			]

	async def retry(self, launch_id: str, agent_id: str) -> str:
		"""Reset a failed agent and resume the pipeline. Returns queued | not_found | not_failed."""
		from src.apps.api.workers.runner import enqueue_orchestrator
		from src.memory.structured.repositories.launch_repo import LaunchRepository

		async with AsyncSessionLocal() as db:
			repo = AgentRepository(db)
			run = next((r for r in await repo.get_by_launch(launch_id) if r.agent_id == agent_id), None)
			if run is None:
				return "not_found"
			if run.status != "failed":
				return "not_failed"
			await repo.reset_agent(launch_id, agent_id)
			await LaunchRepository(db).update_status(launch_id, "running")

		enqueue_orchestrator(launch_id)
		return "queued"


def get_agent_service() -> AgentService:
	return AgentService()

