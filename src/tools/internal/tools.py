"""Internal MCP tool executor.

Provides agents access to launch, prior outputs, and short-term session data.
"""
from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import select

from src.apps.api.models.agent import AgentRun
from src.memory.short_term.session_store import SessionStore
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository
from src.tools._base.base_mcp_server import BaseMCPServer

from .schemas import (
    GetBriefInput,
    GetPriorOutputInput,
    SaveOutputInput,
    SessionDataInput,
    SetSessionDataInput,
)


class InternalToolExecutor(BaseMCPServer):
    async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "get_prior_output":
            payload = self.validate(GetPriorOutputInput, inputs)
            return await self._get_prior_output(payload.launch_id, payload.agent_id)

        if tool_name == "save_output":
            payload = self.validate(SaveOutputInput, inputs)
            return await self._save_output(payload.launch_id, payload.agent_id, payload.output)

        if tool_name == "get_brief":
            payload = self.validate(GetBriefInput, inputs)
            return await self._get_brief(payload.launch_id)

        if tool_name == "get_session_data":
            payload = self.validate(SessionDataInput, inputs)
            store = SessionStore()
            return {"value": await store.get(payload.launch_id, payload.key)}

        if tool_name == "set_session_data":
            payload = self.validate(SetSessionDataInput, inputs)
            store = SessionStore()
            await store.set(payload.launch_id, payload.key, payload.value)
            return {"status": "ok"}

        raise ValueError(f"Unknown internal tool: {tool_name}")

    async def _get_prior_output(self, launch_id: str, agent_id: str) -> dict[str, Any]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(AgentRun).where(
                    AgentRun.launch_id == launch_id,
                    AgentRun.agent_id == agent_id,
                )
            )
            run = result.scalar_one_or_none()
            return {"output": run.output if run else None}

    async def _save_output(self, launch_id: str, agent_id: str, output: dict[str, Any]) -> dict[str, Any]:
        async with AsyncSessionLocal() as db:
            repo = AgentRepository(db)
            await repo.update_status(launch_id, agent_id, status="completed", output=output)
        return {"status": "saved"}

    async def _get_brief(self, launch_id: str) -> dict[str, Any]:
        async with AsyncSessionLocal() as db:
            repo = LaunchRepository(db)
            launch = await repo.get(launch_id)
            if launch is None:
                return {"brief": None}
            return {
                "brief": {
                    "launch_id": launch.launch_id,
                    "product_name": launch.product_name,
                    "description": launch.description,
                    "target_market": launch.target_market,
                    "competitors": list(launch.competitors or []),
                    "launch_date": launch.launch_date,
                    "brief_output": launch.brief_output or {},
                }
            }


def run_sync(tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Sync wrapper for environments that call tool executors synchronously."""
    return asyncio.run(InternalToolExecutor().execute(tool_name, inputs))
