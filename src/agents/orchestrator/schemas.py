"""Orchestrator output schema."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class OrchestratorOutput(BaseModel):
	launch_id: str
	status: Literal["completed", "failed", "hitl_pending"]
	agent_outputs: dict[str, Any]
	hitl_checkpoint: str | None = None

