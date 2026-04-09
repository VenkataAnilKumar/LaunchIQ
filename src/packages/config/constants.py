"""Shared numeric constants used across the Python backend."""
from __future__ import annotations

MAX_CONTEXT_TOKENS: int = 180_000
MAX_OUTPUT_TOKENS: int = 8_192
HITL_TIMEOUT_SECONDS: int = 86_400
CELERY_TASK_TIMEOUT: int = 300
RATE_LIMIT_REQUESTS: int = 60
RATE_LIMIT_WINDOW: int = 60  # seconds
