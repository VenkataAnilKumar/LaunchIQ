"""Workflow state container for orchestrator pipeline runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowState:
	launch_id: str
	brief: dict[str, Any]
	agent_outputs: dict[str, Any] = field(default_factory=dict)
	current_agent: str | None = None
	hitl_pending: bool = False
	hitl_checkpoint: str | None = None
	completed_agents: list[str] = field(default_factory=list)
	failed: bool = False
	failure_reason: str | None = None

	def mark_agent_complete(self, agent_id: str, output: dict[str, Any]) -> None:
		self.agent_outputs[agent_id] = output
		self.current_agent = None
		if agent_id not in self.completed_agents:
			self.completed_agents.append(agent_id)

	def mark_hitl_pending(self, checkpoint: str) -> None:
		self.hitl_pending = True
		self.hitl_checkpoint = checkpoint

	def resume_from_hitl(self, edits: dict[str, Any] | None) -> None:
		if edits and self.completed_agents:
			last_agent = self.completed_agents[-1]
			existing = self.agent_outputs.get(last_agent)
			if isinstance(existing, dict):
				existing.update(edits)
		self.hitl_pending = False
		self.hitl_checkpoint = None

