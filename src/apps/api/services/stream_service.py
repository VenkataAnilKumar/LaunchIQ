"""SSE stream service using Redis pub/sub."""
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from src.memory.short_term.session_store import get_redis


class StreamService:
	async def sse_generator(self, launch_id: str) -> AsyncIterator[str]:
		redis = get_redis()
		channel = f"launch:{launch_id}:events"
		pubsub = redis.pubsub()
		await pubsub.subscribe(channel)

		try:
			yield f"data: {json.dumps({'type': 'connected', 'launch_id': launch_id})}\n\n"
			async for message in pubsub.listen():
				if message["type"] == "message":
					yield f"data: {message['data']}\n\n"
				await asyncio.sleep(0)
		except Exception as exc:
			yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
		finally:
			await pubsub.unsubscribe(channel)
			await pubsub.close()


def get_stream_service() -> StreamService:
	return StreamService()

