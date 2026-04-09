"""Redis-backed HITL state store.

The pipeline polls this key while waiting for a human decision.
Key: hitl:{launch_id}   TTL: 24 h
"""
from __future__ import annotations

import json
from typing import Any

from .session_store import get_redis


class HITLStateStore:
	KEY_PREFIX = "hitl:"
	TTL = 86_400  # 24 hours

	def __init__(self) -> None:
		self.redis = get_redis()

	def _key(self, launch_id: str) -> str:
		return f"{self.KEY_PREFIX}{launch_id}"

	async def set_pending(self, launch_id: str, state: dict[str, Any]) -> None:
		await self.redis.setex(self._key(launch_id), self.TTL, json.dumps(state))

	async def get_pending(self, launch_id: str) -> dict[str, Any] | None:
		data = await self.redis.get(self._key(launch_id))
		return json.loads(data) if data else None

	async def resolve(
		self,
		launch_id: str,
		decision: str,
		edits: dict[str, Any] | None,
	) -> None:
		"""Merge the resolution fields into the existing state record."""
		existing = await self.get_pending(launch_id)
		if existing is None:
			return
		existing["decision"] = decision
		existing["edits"] = edits
		await self.redis.setex(self._key(launch_id), self.TTL, json.dumps(existing))

	async def clear(self, launch_id: str) -> None:
		await self.redis.delete(self._key(launch_id))
