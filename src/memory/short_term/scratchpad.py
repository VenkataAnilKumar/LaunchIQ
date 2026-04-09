"""Per-agent temporary scratchpad backed by Redis.

Key pattern: scratch:{launch_id}:{agent_id}:{key}   TTL: 1 h
Used by agents to persist intermediate reasoning across tool calls.
"""
from __future__ import annotations

from .session_store import get_redis

_TTL = 3600  # 1 hour


class AgentScratchpad:
	KEY_PREFIX = "scratch:"

	def __init__(self) -> None:
		self.redis = get_redis()

	def _key(self, launch_id: str, agent_id: str, key: str) -> str:
		return f"{self.KEY_PREFIX}{launch_id}:{agent_id}:{key}"

	async def write(
		self, launch_id: str, agent_id: str, key: str, value: str
	) -> None:
		await self.redis.setex(self._key(launch_id, agent_id, key), _TTL, value)

	async def read(
		self, launch_id: str, agent_id: str, key: str
	) -> str | None:
		return await self.redis.get(self._key(launch_id, agent_id, key))

	async def clear_all(self, launch_id: str, agent_id: str) -> None:
		"""Delete all scratch keys for a given agent run."""
		pattern = f"{self.KEY_PREFIX}{launch_id}:{agent_id}:*"
		cursor: int = 0
		while True:
			cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
			if keys:
				await self.redis.delete(*keys)
			if cursor == 0:
				break
