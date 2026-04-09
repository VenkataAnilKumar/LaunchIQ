"""Celery tasks for orchestrator and single-agent execution."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from celery import shared_task

from src.agents.orchestrator.agent import OrchestratorAgent
from src.agents.orchestrator.dispatcher import AgentDispatcher
from src.apps.api.models.launch import LaunchStatus
from src.memory.short_term.session_store import SessionStore
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository


def _status_value(status: Any) -> str:
	return status.value if hasattr(status, "value") else str(status)


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,), retry_backoff=True)
def run_orchestrator_task(self, launch_id: str) -> dict[str, str]:
	async def _run() -> dict[str, str]:
		async with AsyncSessionLocal() as db:
			launch_repo = LaunchRepository(db)
			await launch_repo.update_status(launch_id, "running")

		brief = await _load_brief(launch_id)
		payload = {"launch_id": launch_id, **brief}

		try:
			result = await OrchestratorAgent().run(payload)
			status = result.output.get("status", "failed")
			mapped = {
				"completed": "completed",
				"hitl_pending": "hitl_pending",
				"failed": "failed",
			}.get(str(status), "failed")

			async with AsyncSessionLocal() as db:
				launch_repo = LaunchRepository(db)
				await launch_repo.update_status(launch_id, mapped)
			return {"status": str(status), "launch_id": launch_id}
		except Exception as exc:
			async with AsyncSessionLocal() as db:
				launch_repo = LaunchRepository(db)
				await launch_repo.update_status(launch_id, "failed")
			await SessionStore().publish(
				f"launch:{launch_id}:events",
				{
					"type": "agent_failed",
					"launch_id": launch_id,
					"agent_id": "orchestrator",
					"error": str(exc),
					"timestamp": datetime.utcnow().isoformat(),
				},
			)
			raise

	return asyncio.run(_run())


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,), retry_backoff=True)
def run_single_agent_task(self, launch_id: str, agent_id: str) -> dict[str, str]:
	async def _run() -> dict[str, str]:
		dispatcher = AgentDispatcher()

		async with AsyncSessionLocal() as db:
			agent_repo = AgentRepository(db)
			await agent_repo.set_started(launch_id, agent_id)

		brief = await _load_brief(launch_id)
		prior_outputs = await _load_prior_outputs(launch_id)
		payload = {
			"launch_id": launch_id,
			**brief,
			"prior_outputs": prior_outputs,
		}

		try:
			output = await dispatcher.dispatch(agent_id, payload)
			async with AsyncSessionLocal() as db:
				agent_repo = AgentRepository(db)
				await agent_repo.set_completed(launch_id, agent_id, output, tokens_used=0)
			return {"status": "completed", "launch_id": launch_id, "agent_id": agent_id}
		except Exception as exc:
			async with AsyncSessionLocal() as db:
				agent_repo = AgentRepository(db)
				await agent_repo.update_status(
					launch_id,
					agent_id,
					status="failed",
					error=str(exc),
				)
			raise

	return asyncio.run(_run())


async def _load_brief(launch_id: str) -> dict[str, Any]:
	async with AsyncSessionLocal() as db:
		launch_repo = LaunchRepository(db)
		launch = await launch_repo.get(launch_id)
		if launch is None:
			raise ValueError(f"Launch not found: {launch_id}")

		return {
			"product_name": launch.product_name,
			"description": launch.description,
			"target_market": launch.target_market,
			"competitors": list(launch.competitors or []),
			"launch_date": launch.launch_date,
			"brief": launch.brief_output or {},
			"status": _status_value(launch.status),
		}


async def _load_prior_outputs(launch_id: str) -> dict[str, Any]:
	async with AsyncSessionLocal() as db:
		repo = AgentRepository(db)
		runs = await repo.get_by_launch(launch_id)
		return {
			run.agent_id: run.output
			for run in runs
			if run.output is not None and run.status == "completed"
		}
