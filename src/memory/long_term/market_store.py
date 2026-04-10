"""Market data store — vector-searchable market intelligence."""
from __future__ import annotations

import logging
import uuid

from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from src.memory.long_term.qdrant_client import get_qdrant, COLLECTION_MARKET_DATA
from src.memory.long_term.embeddings import embed_text

logger = logging.getLogger(__name__)


class MarketDataStore:
    """Store and retrieve market intelligence data via vector search."""

    async def save(self, launch_id: str, market_data: dict) -> None:
        """Save market data with embedding."""
        try:
            # Embed the recommended positioning + white space as the searchable text
            text_to_embed = (
                f"{market_data.get('recommended_positioning', '')} "
                f"{market_data.get('white_space', '')}"
            ).strip()

            if not text_to_embed:
                logger.warning(f"No text to embed for launch {launch_id}")
                return

            embedding = await embed_text(text_to_embed)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "launch_id": launch_id,
                    **market_data,
                },
            )

            client = get_qdrant()
            await client.upsert(
                collection_name=COLLECTION_MARKET_DATA,
                points=[point],
            )
        except Exception as e:
            logger.warning(f"Failed to save market data for {launch_id}: {e}")

    async def get(self, launch_id: str) -> dict | None:
        """Retrieve market data by launch_id."""
        try:
            client = get_qdrant()
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="payload.launch_id",
                        match=MatchValue(value=launch_id),
                    )
                ]
            )

            result = await client.search(
                collection_name=COLLECTION_MARKET_DATA,
                query_vector=[0.0] * 1536,  # Dummy vector, we filter by launch_id
                query_filter=filter_condition,
                limit=1,
            )

            if result:
                return result[0].payload
            return None
        except Exception as e:
            logger.warning(f"Failed to get market data for {launch_id}: {e}")
            return None

    async def search_similar(self, query: str, limit: int = 5) -> list[dict]:
        """Search for similar market insights by query text."""
        try:
            embedding = await embed_text(query)
            client = get_qdrant()
            results = await client.search(
                collection_name=COLLECTION_MARKET_DATA,
                query_vector=embedding,
                limit=limit,
            )
            return [r.payload for r in results if r.payload]
        except Exception as e:
            logger.warning(f"Failed to search market data: {e}")
            return []
