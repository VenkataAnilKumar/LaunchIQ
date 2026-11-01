"""Dispatch background work either to Celery (default) or in-process (TASK_RUNNER=inline).

Inline mode lets the API run the pipeline in its own event loop, so local
development and tests need no Celery worker.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from src.apps.api.config import get_settings

logger = logging.getLogger(__name__)

_background: set[asyncio.Task[Any]] = set()


def _spawn(coro_factory: Callable[[], Awaitable[Any]], label: str) -> None:
	async def _guarded() -> None:
		try:
			await coro_factory()
		except Exception:
			logger.exception("Inline task failed: %s", label)

	task = asyncio.get_running_loop().create_task(_guarded())
	_background.add(task)  # hold a reference so the task is not garbage-collected
	task.add_done_callback(_background.discard)


def enqueue_orchestrator(launch_id: str) -> None:
	"""Start or resume the orchestrator for a launch."""
	if get_settings().task_runner == "inline":
		from .tasks import execute_orchestrator

		_spawn(lambda: execute_orchestrator(launch_id), f"orchestrator:{launch_id}")
		return
	from .tasks import run_orchestrator_task

	run_orchestrator_task.delay(launch_id)


async def drain_background() -> None:
	"""Wait for inline tasks (tests)."""
	while _background:
		await asyncio.gather(*list(_background), return_exceptions=True)
