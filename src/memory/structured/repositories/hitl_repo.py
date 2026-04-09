"""Repository for HITL checkpoint records."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.api.models.hitl import HITLCheckpointRecord


class HITLRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        launch_id: str,
        checkpoint: str,
        agent_id: str,
        output_preview: dict[str, Any],
    ) -> HITLCheckpointRecord:
        record = HITLCheckpointRecord(
            id=str(uuid.uuid4()),
            launch_id=launch_id,
            checkpoint=checkpoint,
            agent_id=agent_id,
            output_preview=output_preview,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def resolve(
        self,
        launch_id: str,
        decision: str,
        edits: dict[str, Any] | None,
        comment: str | None,
    ) -> None:
        """Resolve the most recent unresolved checkpoint for a launch."""
        await self.db.execute(
            update(HITLCheckpointRecord)
            .where(
                HITLCheckpointRecord.launch_id == launch_id,
                HITLCheckpointRecord.decision.is_(None),
            )
            .values(
                decision=decision,
                edits=edits,
                comment=comment,
                resolved_at=datetime.utcnow(),
            )
        )
        await self.db.commit()
