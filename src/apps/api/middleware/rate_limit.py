"""IP-based Redis rate limiting middleware."""
from __future__ import annotations

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.apps.api.config import get_settings
from src.memory.short_term.session_store import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):  # type: ignore[override]
		path = request.url.path
		if path.startswith("/api/v1/health") or path.startswith("/docs"):
			return await call_next(request)

		settings = get_settings()
		redis = get_redis()
		client_ip = request.client.host if request.client else "unknown"
		key = f"rate:{client_ip}"

		async with redis.pipeline(transaction=True) as pipe:
			await pipe.incr(key)
			await pipe.expire(key, settings.rate_limit_window)
			count, _ = await pipe.execute()

		if int(count) > settings.rate_limit_requests:
			return JSONResponse(
				{"error": "rate_limit_exceeded"},
				status_code=429,
				headers={"Retry-After": str(settings.rate_limit_window)},
			)

		return await call_next(request)

