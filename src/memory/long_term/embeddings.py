"""Text embedding helpers using OpenAI text-embedding-3-small (1536 dims).

Requires settings.openai_api_key to be set. Called by Qdrant upsert paths
when storing and retrieving vector representations of agent outputs.
"""
from __future__ import annotations

import openai

from src.apps.api.config import get_settings


def _get_client() -> openai.AsyncOpenAI:
	return openai.AsyncOpenAI(api_key=get_settings().openai_api_key)


async def embed_text(text: str) -> list[float]:
	"""Return a 1536-dimensional embedding vector for *text*."""
	client = _get_client()
	response = await client.embeddings.create(
		model="text-embedding-3-small",
		input=text,
		dimensions=1536,
	)
	return response.data[0].embedding


async def embed_batch(texts: list[str]) -> list[list[float]]:
	"""Return embedding vectors for a list of texts in input order."""
	client = _get_client()
	response = await client.embeddings.create(
		model="text-embedding-3-small",
		input=texts,
		dimensions=1536,
	)
	# API may reorder items; sort by index to guarantee input order.
	return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
