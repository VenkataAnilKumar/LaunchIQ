"""Celery application configuration for async pipeline jobs."""
from __future__ import annotations

from celery import Celery

from src.apps.api.config import get_settings

settings = get_settings()

celery_app = Celery(
	"launchiq",
	broker=settings.redis_url,
	backend=settings.redis_url,
	include=["src.apps.api.workers.tasks"],
)

celery_app.conf.update(
	task_serializer="json",
	result_serializer="json",
	accept_content=["json"],
	task_acks_late=True,
	worker_prefetch_multiplier=1,
)

