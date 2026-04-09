"""Repository for the strategy section of Launch.brief_output."""
from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from .launch_repo import LaunchRepository


class StrategyRepository:
    """Read/write the 'strategy' key inside Launch.brief_output."""

    _SECTION = "strategy"

    def __init__(self, db: AsyncSession) -> None:
        self._launches = LaunchRepository(db)

    async def get(self, launch_id: str) -> dict[str, Any] | None:
        launch = await self._launches.get(launch_id)
        if launch is None or not launch.brief_output:
            return None
        return launch.brief_output.get(self._SECTION)

    async def save(self, launch_id: str, data: dict[str, Any]) -> None:
        launch = await self._launches.get(launch_id)
        brief: dict[str, Any] = dict(launch.brief_output or {})
        brief[self._SECTION] = data
        await self._launches.save_brief_output(launch_id, brief)
