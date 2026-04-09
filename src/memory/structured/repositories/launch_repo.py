"""Repository for Launch records."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.api.models.launch import Launch, LaunchStatus


class LaunchRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_id: str, data: dict[str, Any]) -> Launch:
        launch = Launch(
            launch_id=str(uuid.uuid4()),
            user_id=user_id,
            **data,
        )
        self.db.add(launch)
        await self.db.commit()
        await self.db.refresh(launch)
        return launch

    async def get(self, launch_id: str) -> Launch | None:
        result = await self.db.execute(
            select(Launch).where(Launch.launch_id == launch_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Launch]:
        result = await self.db.execute(
            select(Launch)
            .where(Launch.user_id == user_id)
            .order_by(Launch.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, launch_id: str, status: LaunchStatus) -> None:
        await self.db.execute(
            update(Launch)
            .where(Launch.launch_id == launch_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def save_brief_output(self, launch_id: str, output: dict[str, Any]) -> None:
        await self.db.execute(
            update(Launch)
            .where(Launch.launch_id == launch_id)
            .values(brief_output=output, updated_at=datetime.utcnow())
        )
        await self.db.commit()
