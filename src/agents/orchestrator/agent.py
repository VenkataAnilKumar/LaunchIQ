"""Orchestrator agent implementation."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent
from src.memory.short_term.hitl_state import HITLStateStore
from src.memory.short_term.session_store import SessionStore

from .dispatcher import AgentDispatcher
from .schemas import OrchestratorOutput
from .workflow_state import WorkflowState


def _load_system_prompt() -> str:
	prompt_path = Path(__file__).parent / "prompts" / "system.md"
	if not prompt_path.exists():
		return "You are the LaunchIQ orchestrator."
	return prompt_path.read_text(encoding="utf-8")


class OrchestratorAgent(BaseAgent):
	PIPELINE_SEQUENCE = [
		"market_intelligence",
		"audience_insight",
		"launch_strategy",
		"content_generation",
	]
	HITL_AFTER = {
		"market_intelligence": "brief_review",
		"launch_strategy": "strategy_review",
	}

	def __init__(self) -> None:
		config = AgentConfig(
			agent_id="orchestrator",
			model="claude-opus-4-6",
			enable_thinking=True,
			thinking_budget=8000,
			system_prompt=_load_system_prompt(),
		)
		super().__init__(config)
		self.dispatcher = AgentDispatcher()
		self._session_store = SessionStore()
		self._hitl_store = HITLStateStore()

	def get_output_schema(self) -> type[BaseModel]:
		return OrchestratorOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		launch_id = str(payload.get("launch_id", ""))
		if not launch_id:
			raise ValueError("Orchestrator payload must include launch_id")

		state = WorkflowState(launch_id=launch_id, brief=payload)

		for agent_id in self.PIPELINE_SEQUENCE:
			state.current_agent = agent_id
			await self._publish_event(
				launch_id,
				{
					"type": "agent_started",
					"launch_id": launch_id,
					"agent_id": agent_id,
					"timestamp": datetime.utcnow().isoformat(),
				},
			)

			agent_payload = {
				**payload,
				"launch_id": launch_id,
				"prior_outputs": state.agent_outputs,
			}

			output: dict[str, Any] | None = None
			last_error: Exception | None = None
			for _attempt in range(2):
				try:
					output = await self.dispatcher.dispatch(agent_id, agent_payload)
					last_error = None
					break
				except Exception as exc:  # noqa: PERF203
					last_error = exc

			if output is None:
				state.failed = True
				state.failure_reason = str(last_error) if last_error else "unknown_error"
				await self._publish_event(
					launch_id,
					{
						"type": "agent_failed",
						"launch_id": launch_id,
						"agent_id": agent_id,
						"error": state.failure_reason,
						"timestamp": datetime.utcnow().isoformat(),
					},
				)
				break

			state.mark_agent_complete(agent_id, output)
			await self._publish_event(
				launch_id,
				{
					"type": "agent_completed",
					"launch_id": launch_id,
					"agent_id": agent_id,
					"output": output,
					"timestamp": datetime.utcnow().isoformat(),
				},
			)

			checkpoint = self.HITL_AFTER.get(agent_id)
			if checkpoint:
				await self._pause_for_hitl(state, checkpoint, output)
				resolution = await self._wait_for_hitl_resolution(launch_id)

				if resolution is None:
					state.failed = True
					state.failure_reason = "HITL timeout"
					break

				decision = resolution.get("decision")
				edits = resolution.get("edits")
				if decision == "reject":
					state.failed = True
					state.failure_reason = "Rejected during HITL review"
					state.resume_from_hitl(None)
					break

				state.resume_from_hitl(edits if isinstance(edits, dict) else None)
				await self._hitl_store.clear(launch_id)

		if state.failed:
			status = "failed"
			hitl_checkpoint = state.hitl_checkpoint
		elif state.hitl_pending:
			status = "hitl_pending"
			hitl_checkpoint = state.hitl_checkpoint
		else:
			status = "completed"
			hitl_checkpoint = None

		output_model = OrchestratorOutput(
			launch_id=launch_id,
			status=status,
			agent_outputs=state.agent_outputs,
			hitl_checkpoint=hitl_checkpoint,
		)

		return AgentResult(
			agent_id=self.config.agent_id,
			output=output_model.model_dump(),
			hitl_required=status == "hitl_pending",
			hitl_checkpoint=hitl_checkpoint,
		)

	async def _pause_for_hitl(
		self,
		state: WorkflowState,
		checkpoint: str,
		output: dict[str, Any],
	) -> None:
		state.mark_hitl_pending(checkpoint)
		pending = {
			"launch_id": state.launch_id,
			"checkpoint": checkpoint,
			"agent_id": state.completed_agents[-1] if state.completed_agents else "unknown",
			"output_preview": output,
			"created_at": datetime.utcnow().isoformat(),
		}
		await self._hitl_store.set_pending(state.launch_id, pending)
		await self._publish_event(
			state.launch_id,
			{
				"type": "hitl_required",
				**pending,
			},
		)

	async def _wait_for_hitl_resolution(
		self,
		launch_id: str,
		timeout: int = 86400,
	) -> dict[str, Any] | None:
		elapsed = 0
		while elapsed < timeout:
			pending = await self._hitl_store.get_pending(launch_id)
			if pending and pending.get("decision"):
				return pending
			await asyncio.sleep(2)
			elapsed += 2
		return None

	async def _publish_event(self, launch_id: str, event: dict[str, Any]) -> None:
		await self._session_store.publish(f"launch:{launch_id}:events", event)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)

