"""Launch Strategy worker agent."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent

from .schemas import LaunchStrategyOutput


def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class LaunchStrategyAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="launch_strategy",
				model="opus",
				enable_thinking=True,
				thinking_budget=10000,
				system_prompt=_load_prompt("system.md"),
			)
		)

	def get_output_schema(self) -> type[BaseModel]:
		return LaunchStrategyOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		prior = payload.get("prior_outputs", {}) or {}
		market_data = prior.get("market_intelligence", {})
		personas = prior.get("audience_insight", {})

		user_msg = (
			"Create launch strategy JSON for this launch.\n"
			f"{self._brief_block(payload)}"
			f"market_data: {json.dumps(market_data)}\n"
			f"personas: {json.dumps(personas)}\n"
			f"strategy_guide:\n{_load_prompt('strategy.md')}"
		)

		messages = self._build_messages(
			user_msg,
			context={"market_data": market_data, "personas": personas},
		)

		validated, _, thinking = await self._generate_validated(messages)
		return self.make_result(validated, thinking=thinking)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)


