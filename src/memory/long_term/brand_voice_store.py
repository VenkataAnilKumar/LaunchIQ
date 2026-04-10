"""Brand voice store — vector-searchable brand voice guidelines."""
from __future__ import annotations

import logging
import uuid

from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from src.memory.long_term.qdrant_client import get_qdrant, COLLECTION_BRAND_VOICE
from src.memory.long_term.embeddings import embed_text

logger = logging.getLogger(__name__)


class BrandVoiceStore:
    """Store and retrieve brand voice guidelines via vector search."""

    async def save(self, launch_id: str, brand_voice: dict) -> None:
        """Save brand voice with embedding."""
        try:
            # Embed the brand voice notes as the searchable text
            text_to_embed = brand_voice.get("brand_voice_notes", "").strip()

            if not text_to_embed:
                logger.warning(f"No brand voice notes for launch {launch_id}")
                return

            embedding = await embed_text(text_to_embed)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "launch_id": launch_id,
                    **brand_voice,
                },
            )

            client = get_qdrant()
            await client.upsert(
                collection_name=COLLECTION_BRAND_VOICE,
                points=[point],
            )
        except Exception as e:
            logger.warning(f"Failed to save brand voice for {launch_id}: {e}")

    async def get(self, launch_id: str) -> dict | None:
        """Retrieve brand voice by launch_id."""
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
                collection_name=COLLECTION_BRAND_VOICE,
                query_vector=[0.0] * 1536,  # Dummy vector, we filter by launch_id
                query_filter=filter_condition,
                limit=1,
            )

            if result:
                return result[0].payload
            return None
        except Exception as e:
            logger.warning(f"Failed to get brand voice for {launch_id}: {e}")
            return None

    async def find_similar_voice(
        self, sample_text: str, limit: int = 3
    ) -> list[dict]:
        """Find launches with similar brand voice (for reuse across launches)."""
        try:
            embedding = await embed_text(sample_text)
            client = get_qdrant()
            results = await client.search(
                collection_name=COLLECTION_BRAND_VOICE,
                query_vector=embedding,
                limit=limit,
            )
            return [r.payload for r in results if r.payload]
        except Exception as e:
            logger.warning(f"Failed to find similar brand voices: {e}")
            return []
