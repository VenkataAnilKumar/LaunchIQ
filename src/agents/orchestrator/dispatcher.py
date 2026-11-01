"""Dynamic agent dispatcher used by the orchestrator and worker tasks."""
from __future__ import annotations

import importlib
from typing import Any

from src.agents._base.base_agent import AgentResult


class AgentDispatcher:
	AGENT_MODULE_MAP: dict[str, str] = {
		"market_intelligence": "src.agents.market_intelligence.agent",
		"audience_insight": "src.agents.audience_insight.agent",
		"launch_strategy": "src.agents.launch_strategy.agent",
		"content_generation": "src.agents.content_generation.agent",
		"analytics_feedback": "src.agents.analytics_feedback.agent",
	}

	async def dispatch(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
		return (await self.dispatch_result(agent_id, payload)).output

	async def dispatch_result(self, agent_id: str, payload: dict[str, Any]) -> AgentResult:
		"""Run an agent and return the full AgentResult (output + token/cost usage)."""
		module_path = self.AGENT_MODULE_MAP.get(agent_id)
		if not module_path:
			raise ValueError(f"Unknown agent_id: {agent_id}")

		module = importlib.import_module(module_path)
		class_name = self._to_class_name(agent_id)
		agent_cls = getattr(module, class_name)
		agent = agent_cls()
		result = await agent.run(payload)

		# BaseAgent.run returns AgentResult; preserve compatibility with dict returns.
		if isinstance(result, AgentResult):
			return result
		if isinstance(result, dict):
			return AgentResult(agent_id=agent_id, output=result)
		raise TypeError(f"Unexpected agent result type for {agent_id}: {type(result)!r}")

	def _to_class_name(self, agent_id: str) -> str:
		return "".join(part.capitalize() for part in agent_id.split("_")) + "Agent"

