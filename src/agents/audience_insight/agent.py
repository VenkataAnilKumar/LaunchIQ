"""Audience Insight worker agent."""
from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent

from .schemas import AudienceInsightOutput


def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class AudienceInsightAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="audience_insight",
				model="sonnet",
				system_prompt=_load_prompt("system.md"),
			)
		)

	def get_output_schema(self) -> type[BaseModel]:
		return AudienceInsightOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		prior_outputs = payload.get("prior_outputs", {}) or {}
		market_data = prior_outputs.get("market_intelligence", {})

		user_msg = (
			"Generate audience insights as strict JSON.\n"
			f"{self._brief_block(payload)}"
			f"market_data: {json.dumps(market_data)}\n"
			f"persona_guide:\n{_load_prompt('persona.md')}"
		)

		messages = self._build_messages(user_msg, context={"market_data": market_data})
		validated, _, _ = await self._generate_validated(messages)
		return self.make_result(validated)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)


