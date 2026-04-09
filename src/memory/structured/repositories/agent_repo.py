"""Repository for AgentRun records."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.api.models.agent import AgentRun


class AgentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, launch_id: str, agent_id: str) -> AgentRun:
        run = AgentRun(launch_id=launch_id, agent_id=agent_id, status="pending")
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_by_launch(self, launch_id: str) -> list[AgentRun]:
        result = await self.db.execute(
            select(AgentRun).where(AgentRun.launch_id == launch_id)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        launch_id: str,
        agent_id: str,
        status: str,
        output: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": status}
        if output is not None:
            values["output"] = output
        if error is not None:
            values["error"] = error
        await self.db.execute(
            update(AgentRun)
            .where(AgentRun.launch_id == launch_id, AgentRun.agent_id == agent_id)
            .values(**values)
        )
        await self.db.commit()

    async def set_started(self, launch_id: str, agent_id: str) -> None:
        await self.db.execute(
            update(AgentRun)
            .where(AgentRun.launch_id == launch_id, AgentRun.agent_id == agent_id)
            .values(status="running", started_at=datetime.utcnow())
        )
        await self.db.commit()

    async def set_completed(
        self,
        launch_id: str,
        agent_id: str,
        output: dict[str, Any],
        tokens_used: int,
    ) -> None:
        await self.db.execute(
            update(AgentRun)
            .where(AgentRun.launch_id == launch_id, AgentRun.agent_id == agent_id)
            .values(
                status="completed",
                output=output,
                tokens_used=tokens_used,
                completed_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def reset_agent(self, launch_id: str, agent_id: str) -> bool:
        result = await self.db.execute(
            update(AgentRun)
            .where(AgentRun.launch_id == launch_id, AgentRun.agent_id == agent_id)
            .values(
                status="pending",
                output=None,
                error=None,
                started_at=None,
                completed_at=None,
            )
        )
        await self.db.commit()
        return result.rowcount > 0
