"""Persistence boundary for the orchestrator.

The orchestrator never talks to the database directly: it uses a ``RunStore``.
``DbRunStore`` writes to PostgreSQL/SQLite (production + local runs);
``MemoryRunStore`` keeps everything in dicts (unit tests, no I/O).
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol


class RunStore(Protocol):
    async def get_agent_states(self, launch_id: str) -> dict[str, dict[str, Any]]: ...
    async def mark_started(self, launch_id: str, agent_id: str) -> None: ...
    async def mark_completed(
        self, launch_id: str, agent_id: str, output: dict[str, Any], usage: dict[str, Any]
    ) -> None: ...
    async def mark_failed(self, launch_id: str, agent_id: str, error: str) -> None: ...
    async def get_checkpoint(self, launch_id: str, checkpoint: str) -> dict[str, Any] | None: ...
    async def create_checkpoint(
        self, launch_id: str, checkpoint: str, agent_id: str, output_preview: dict[str, Any]
    ) -> dict[str, Any]: ...
    async def set_launch_status(self, launch_id: str, status: str) -> None: ...
    async def save_final_output(self, launch_id: str, output: dict[str, Any]) -> None: ...


class MemoryRunStore:
    """In-memory RunStore for tests."""

    def __init__(self) -> None:
        self.agents: dict[tuple[str, str], dict[str, Any]] = {}
        self.checkpoints: dict[tuple[str, str], dict[str, Any]] = {}
        self.launch_status: dict[str, str] = {}
        self.final_output: dict[str, dict[str, Any]] = {}

    async def get_agent_states(self, launch_id: str) -> dict[str, dict[str, Any]]:
        return {a: dict(v) for (lid, a), v in self.agents.items() if lid == launch_id}

    async def mark_started(self, launch_id: str, agent_id: str) -> None:
        self.agents[(launch_id, agent_id)] = {"status": "running", "output": None, "cost_usd": 0.0}

    async def mark_completed(self, launch_id, agent_id, output, usage) -> None:
        self.agents[(launch_id, agent_id)] = {
            "status": "completed",
            "output": output,
            "tokens_used": usage.get("tokens_used", 0),
            "cost_usd": usage.get("cost_usd", 0.0),
        }

    async def mark_failed(self, launch_id: str, agent_id: str, error: str) -> None:
        prev = self.agents.get((launch_id, agent_id), {})
        self.agents[(launch_id, agent_id)] = {**prev, "status": "failed", "error": error}

    async def get_checkpoint(self, launch_id: str, checkpoint: str) -> dict[str, Any] | None:
        rec = self.checkpoints.get((launch_id, checkpoint))
        return dict(rec) if rec else None

    async def create_checkpoint(self, launch_id, checkpoint, agent_id, output_preview) -> dict[str, Any]:
        rec = {
            "launch_id": launch_id,
            "checkpoint": checkpoint,
            "agent_id": agent_id,
            "output_preview": output_preview,
            "decision": None,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.checkpoints[(launch_id, checkpoint)] = rec
        return dict(rec)

    async def set_launch_status(self, launch_id: str, status: str) -> None:
        self.launch_status[launch_id] = status

    async def save_final_output(self, launch_id: str, output: dict[str, Any]) -> None:
        self.final_output[launch_id] = output

    # test helper
    def resolve(self, launch_id: str, checkpoint: str, decision: str) -> None:
        self.checkpoints[(launch_id, checkpoint)]["decision"] = decision


class DbRunStore:
    """RunStore backed by the structured (SQL) memory layer."""

    async def get_agent_states(self, launch_id: str) -> dict[str, dict[str, Any]]:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.agent_repo import AgentRepository

        async with AsyncSessionLocal() as db:
            runs = await AgentRepository(db).get_by_launch(launch_id)
        return {
            r.agent_id: {
                "status": r.status,
                "output": r.output,
                "tokens_used": r.tokens_used or 0,
                "cost_usd": r.cost_usd or 0.0,
                "error": r.error,
            }
            for r in runs
        }

    async def _ensure_row(self, db, launch_id: str, agent_id: str) -> None:
        from src.memory.structured.repositories.agent_repo import AgentRepository

        repo = AgentRepository(db)
        if not any(r.agent_id == agent_id for r in await repo.get_by_launch(launch_id)):
            await repo.create(launch_id=launch_id, agent_id=agent_id)

    async def mark_started(self, launch_id: str, agent_id: str) -> None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.agent_repo import AgentRepository

        async with AsyncSessionLocal() as db:
            await self._ensure_row(db, launch_id, agent_id)
            await AgentRepository(db).set_started(launch_id, agent_id)

    async def mark_completed(self, launch_id, agent_id, output, usage) -> None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.agent_repo import AgentRepository

        async with AsyncSessionLocal() as db:
            await AgentRepository(db).set_completed(
                launch_id,
                agent_id,
                output,
                tokens_used=int(usage.get("tokens_used", 0)),
                cost_usd=float(usage.get("cost_usd", 0.0)),
            )

    async def mark_failed(self, launch_id: str, agent_id: str, error: str) -> None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.agent_repo import AgentRepository

        async with AsyncSessionLocal() as db:
            await AgentRepository(db).update_status(launch_id, agent_id, status="failed", error=error)

    async def get_checkpoint(self, launch_id: str, checkpoint: str) -> dict[str, Any] | None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.hitl_repo import HITLRepository

        async with AsyncSessionLocal() as db:
            rec = await HITLRepository(db).get_latest(launch_id, checkpoint)
        if rec is None:
            return None
        return {
            "launch_id": rec.launch_id,
            "checkpoint": rec.checkpoint,
            "agent_id": rec.agent_id,
            "output_preview": rec.output_preview,
            "decision": rec.decision,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }

    async def create_checkpoint(self, launch_id, checkpoint, agent_id, output_preview) -> dict[str, Any]:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.hitl_repo import HITLRepository

        async with AsyncSessionLocal() as db:
            rec = await HITLRepository(db).create(launch_id, checkpoint, agent_id, output_preview)
        return {
            "launch_id": launch_id,
            "checkpoint": checkpoint,
            "agent_id": agent_id,
            "output_preview": output_preview,
            "decision": None,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }

    async def set_launch_status(self, launch_id: str, status: str) -> None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.launch_repo import LaunchRepository

        async with AsyncSessionLocal() as db:
            await LaunchRepository(db).update_status(launch_id, status)

    async def save_final_output(self, launch_id: str, output: dict[str, Any]) -> None:
        from src.memory.structured.database import AsyncSessionLocal
        from src.memory.structured.repositories.launch_repo import LaunchRepository

        async with AsyncSessionLocal() as db:
            await LaunchRepository(db).save_brief_output(launch_id, output)
