"""Persona store — vector-searchable buyer personas."""
from __future__ import annotations

import logging
import uuid

from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from src.memory.long_term.qdrant_client import get_qdrant, COLLECTION_PERSONAS
from src.memory.long_term.embeddings import embed_text

logger = logging.getLogger(__name__)


class PersonaStore:
    """Store and retrieve buyer personas via vector search."""

    async def save(self, launch_id: str, personas: list[dict]) -> None:
        """Save personas with embeddings."""
        try:
            client = get_qdrant()
            points = []

            for persona in personas:
                # Embed the message hook + pain points as searchable text
                text_to_embed = (
                    f"{persona.get('message_hook', '')} "
                    f"{' '.join(persona.get('pain_points', []))}"
                ).strip()

                if not text_to_embed:
                    logger.warning(f"No text to embed for persona {persona.get('name')}")
                    continue

                embedding = await embed_text(text_to_embed)

                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "launch_id": launch_id,
                        "persona_name": persona.get("name", "Unknown"),
                        **persona,
                    },
                )
                points.append(point)

            if points:
                await client.upsert(
                    collection_name=COLLECTION_PERSONAS,
                    points=points,
                )
        except Exception as e:
            logger.warning(f"Failed to save personas for {launch_id}: {e}")

    async def get_by_launch(self, launch_id: str) -> list[dict]:
        """Retrieve all personas for a launch."""
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
                collection_name=COLLECTION_PERSONAS,
                query_vector=[0.0] * 1536,  # Dummy vector, we filter by launch_id
                query_filter=filter_condition,
                limit=10,
            )

            return [r.payload for r in result if r.payload]
        except Exception as e:
            logger.warning(f"Failed to get personas for {launch_id}: {e}")
            return []

    async def find_similar_persona(
        self, description: str, limit: int = 3
    ) -> list[dict]:
        """Find personas similar to a given description (across all launches)."""
        try:
            embedding = await embed_text(description)
            client = get_qdrant()
            results = await client.search(
                collection_name=COLLECTION_PERSONAS,
                query_vector=embedding,
                limit=limit,
            )
            return [r.payload for r in results if r.payload]
        except Exception as e:
            logger.warning(f"Failed to find similar personas: {e}")
            return []
