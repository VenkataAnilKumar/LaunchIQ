"""Redis-backed session store and pub/sub publisher.

All keys follow the pattern: session:{launch_id}:{key}
SSE events are published to: launch:{launch_id}:events
"""
from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from src.apps.api.config import get_settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
	"""Return a singleton Redis client (lazy-initialised)."""
	global _redis
	if _redis is None:
		settings = get_settings()
		_redis = aioredis.from_url(settings.redis_url, decode_responses=True)
	return _redis


class SessionStore:
	"""Per-launch key/value store with TTL and pub/sub support."""

	KEY_PREFIX = "session:"
	DEFAULT_TTL = 3600  # 1 hour

	def __init__(self) -> None:
		self.redis = get_redis()

	async def set(
		self,
		launch_id: str,
		key: str,
		value: dict[str, Any],
		ttl: int = DEFAULT_TTL,
	) -> None:
		field = f"{self.KEY_PREFIX}{launch_id}:{key}"
		await self.redis.setex(field, ttl, json.dumps(value))

	async def get(self, launch_id: str, key: str) -> dict[str, Any] | None:
		field = f"{self.KEY_PREFIX}{launch_id}:{key}"
		data = await self.redis.get(field)
		return json.loads(data) if data else None

	async def delete(self, launch_id: str, key: str) -> None:
		await self.redis.delete(f"{self.KEY_PREFIX}{launch_id}:{key}")

	async def publish(self, channel: str, event: dict[str, Any]) -> None:
		"""Publish a JSON-encoded event to a Redis pub/sub channel."""
		await self.redis.publish(channel, json.dumps(event))
