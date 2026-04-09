"""Market Intelligence worker agent."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent
from src.tools.tavily_search.tools import TavilySearchExecutor

from .schemas import MarketIntelligenceOutput

TAVILY_TOOL = {
	"name": "tavily_search",
	"description": "Search the web for market, competitor, and trend signals.",
	"input_schema": {
		"type": "object",
		"properties": {
			"query": {"type": "string"},
			"max_results": {"type": "integer", "minimum": 1, "maximum": 10},
			"search_depth": {"type": "string"},
		},
		"required": ["query"],
	},
}


def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class MarketIntelligenceAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="market_intelligence",
				model="claude-sonnet-4-6",
				max_tokens=4096,
				tools=[TAVILY_TOOL],
				system_prompt=_load_prompt("system.md"),
			)
		)

	def get_output_schema(self) -> type[BaseModel]:
		return MarketIntelligenceOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		user_msg = (
			"Generate market intelligence JSON for this launch brief:\n"
			f"product_name: {payload.get('product_name', '')}\n"
			f"description: {payload.get('description', '')}\n"
			f"target_market: {payload.get('target_market', '')}\n"
			f"competitors: {payload.get('competitors', [])}\n"
			f"research_guidance:\n{_load_prompt('research.md')}\n"
			f"analysis_guidance:\n{_load_prompt('analyze.md')}"
		)

		messages = self._build_messages(user_msg)
		final_text, tool_calls, thinking = await self._call_with_tools(
			messages,
			TavilySearchExecutor(),
		)

		output_dict = self._extract_json(final_text)
		validated = self._validate_output(output_dict)
		return AgentResult(
			agent_id=self.config.agent_id,
			output=validated,
			thinking=thinking,
			tool_calls=tool_calls,
		)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)

	def _extract_json(self, text: str) -> dict[str, Any]:
		fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		raw = fenced.group(1) if fenced else text.strip()
		# Fallback to first JSON object if model included extra text.
		if not raw.startswith("{"):
			match = re.search(r"(\{.*\})", raw, re.DOTALL)
			if match:
				raw = match.group(1)
		return json.loads(raw)

