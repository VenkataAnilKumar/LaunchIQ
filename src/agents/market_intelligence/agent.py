"""Market Intelligence worker agent."""
from __future__ import annotations

import json
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
				model="sonnet",
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
			f"{self._brief_block(payload)}"
			f"research_guidance:\n{_load_prompt('research.md')}\n"
			f"analysis_guidance:\n{_load_prompt('analyze.md')}"
		)

		messages = self._build_messages(user_msg)
		validated, tool_calls, thinking = await self._generate_validated(
			messages, TavilySearchExecutor()
		)
		return self.make_result(validated, thinking=thinking, tool_calls=tool_calls)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)


