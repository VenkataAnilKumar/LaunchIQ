"""Qdrant async client singleton and collection helpers.

Collections are created on first use via ensure_collections().
All vectors use cosine distance with 1536 dimensions
(matching text-embedding-3-small / voyage-3).
"""
from __future__ import annotations

from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.apps.api.config import get_settings

COLLECTION_MARKET_DATA = "market_data"
COLLECTION_PERSONAS = "personas"
COLLECTION_BRAND_VOICE = "brand_voice"

VECTOR_SIZE = 1536

_qdrant: AsyncQdrantClient | None = None


def get_qdrant() -> AsyncQdrantClient:
	"""Return a singleton AsyncQdrantClient (lazy-initialised)."""
	global _qdrant
	if _qdrant is None:
		settings = get_settings()
		_qdrant = AsyncQdrantClient(
			url=settings.qdrant_url,
			api_key=settings.qdrant_api_key or None,
		)
	return _qdrant


async def ensure_collections() -> None:
	"""Create Qdrant collections if they do not already exist."""
	client = get_qdrant()
	for name in (COLLECTION_MARKET_DATA, COLLECTION_PERSONAS, COLLECTION_BRAND_VOICE):
		if not await client.collection_exists(name):
			await client.create_collection(
				collection_name=name,
				vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
			)


async def upsert(
	collection: str,
	id: str,
	vector: list[float],
	payload: dict[str, Any],
) -> None:
	client = get_qdrant()
	await client.upsert(
		collection_name=collection,
		points=[PointStruct(id=id, vector=vector, payload=payload)],
	)


async def search(
	collection: str,
	vector: list[float],
	limit: int = 5,
) -> list[dict[str, Any]]:
	"""Return the payload dicts of the top *limit* nearest neighbours."""
	client = get_qdrant()
	results = await client.search(
		collection_name=collection,
		query_vector=vector,
		limit=limit,
	)
	return [hit.payload for hit in results if hit.payload]
