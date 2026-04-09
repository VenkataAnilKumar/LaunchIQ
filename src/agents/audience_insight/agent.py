"""Audience Insight worker agent."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, AsyncIterator

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
				model="claude-sonnet-4-6",
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
			f"market_data: {json.dumps(market_data)}\n"
			f"persona_guide:\n{_load_prompt('persona.md')}"
		)

		messages = self._build_messages(user_msg, context={"market_data": market_data})
		response = self.client.messages.create(**self._make_api_params(messages))

		text_parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
		final_text = "".join(text_parts)

		output_dict = self._extract_json(final_text)
		validated = self._validate_output(output_dict)
		usage = getattr(response, "usage", None)
		tokens = int(getattr(usage, "output_tokens", 0) or 0)

		return AgentResult(
			agent_id=self.config.agent_id,
			output=validated,
			tokens_used=tokens,
		)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)

	def _extract_json(self, text: str) -> dict[str, Any]:
		fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		raw = fenced.group(1) if fenced else text.strip()
		if not raw.startswith("{"):
			match = re.search(r"(\{.*\})", raw, re.DOTALL)
			if match:
				raw = match.group(1)
		return json.loads(raw)

