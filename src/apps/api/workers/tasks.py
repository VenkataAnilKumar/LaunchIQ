"""Celery tasks for the orchestrator pipeline."""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from src.agents.orchestrator.agent import OrchestratorAgent
from src.memory.short_term.session_store import SessionStore
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.launch_repo import LaunchRepository

from .celery_app import celery_app

logger = logging.getLogger(__name__)


def _status_value(status: Any) -> str:
	return status.value if hasattr(status, "value") else str(status)


async def execute_orchestrator(launch_id: str) -> dict[str, Any]:
	"""Run (or resume) the pipeline until it finishes or needs a human decision."""
	brief = await _load_brief(launch_id)
	payload = {"launch_id": launch_id, **brief}
	try:
		result = await OrchestratorAgent().run(payload)
	except Exception as exc:
		logger.exception("Orchestrator crashed for %s", launch_id)
		async with AsyncSessionLocal() as db:
			await LaunchRepository(db).update_status(launch_id, "failed")
		try:
			await SessionStore().publish(
				f"launch:{launch_id}:events",
				{
					"type": "launch_failed",
					"launch_id": launch_id,
					"reason": str(exc),
					"timestamp": datetime.now(UTC).isoformat(),
				},
			)
		except Exception:
			logger.warning("Could not publish failure event for %s", launch_id)
		raise
	return {"status": str(result.output.get("status")), "launch_id": launch_id}


# Bound to our configured app explicitly: @shared_task would fall back to Celery's default
# AMQP app in any process (e.g. the API) that has not imported celery_app first.
@celery_app.task(bind=True, max_retries=1, autoretry_for=(Exception,), retry_backoff=True)
def run_orchestrator_task(self, launch_id: str) -> dict[str, Any]:
	return asyncio.run(execute_orchestrator(launch_id))


async def _load_brief(launch_id: str) -> dict[str, Any]:
	async with AsyncSessionLocal() as db:
		launch = await LaunchRepository(db).get(launch_id)
		if launch is None:
			raise ValueError(f"Launch not found: {launch_id}")
		return {
			"product_name": launch.product_name,
			"description": launch.description,
			"target_market": launch.target_market,
			"competitors": list(launch.competitors or []),
			"launch_date": launch.launch_date,
		}
