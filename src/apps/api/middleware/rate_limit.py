"""IP-based Redis rate limiting middleware."""
from __future__ import annotations

import logging

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.apps.api.config import get_settings
from src.memory.short_term.session_store import get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):  # type: ignore[override]
		path = request.url.path
		if path.startswith("/api/v1/health") or path.startswith("/docs") or path.endswith("/stream"):
			return await call_next(request)

		settings = get_settings()
		client_ip = request.client.host if request.client else "unknown"
		key = f"rate:{client_ip}"

		# Fixed window: the TTL is set once, when the key is created. Refreshing it on every
		# request would keep a busy client blocked forever. If Redis is unavailable the
		# limiter fails open (logged) rather than taking the whole API down.
		try:
			redis = get_redis()
			count = await redis.incr(key)
			if int(count) == 1:
				await redis.expire(key, settings.rate_limit_window)
		except Exception as exc:
			logger.warning("Rate limiter unavailable; allowing request: %s", exc)
			return await call_next(request)

		if int(count) > settings.rate_limit_requests:
			return JSONResponse(
				{"error": "rate_limit_exceeded"},
				status_code=429,
				headers={"Retry-After": str(settings.rate_limit_window)},
			)

		return await call_next(request)

