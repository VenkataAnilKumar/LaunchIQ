"""Analytics & Feedback worker agent."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent
from src.agents._base.llm import AgentError

from .schemas import AnalyticsOutput

def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class AnalyticsFeedbackAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="analytics_feedback",
				model="haiku",
				system_prompt=_load_prompt("system.md"),
			)
		)

	def get_output_schema(self) -> type[BaseModel]:
		return AnalyticsOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		"""Analyze REAL measurements supplied by the user.

		Without measurements there is nothing honest to analyze, so this refuses instead of
		inventing performance numbers (the GA4 connector is not implemented yet).
		"""
		metrics = payload.get("metrics")
		if not isinstance(metrics, dict) or not metrics:
			raise AgentError(
				"Analytics needs measured results: pass `metrics` "
				"(e.g. sessions, conversions, engagement_rate, per-content CTR)."
			)
		prior = payload.get("prior_outputs", {}) or {}
		content = prior.get("content_generation", {}) or {}
		titles = [
			f"{i.get('format')}/{i.get('variant')}: {i.get('headline')}"
			for key in ("email_sequence", "social_posts", "ad_copy")
			for i in content.get(key, [])
		]
		user_msg = (
			"Analyze launch performance from these measured results and return strict JSON.\n"
			f"{self._brief_block(payload)}"
			f"measured_metrics: {json.dumps(metrics)}\n"
			f"content_pieces: {json.dumps(titles)}\n"
			f"recommendation_guide:\n{_load_prompt('recommend.md')}"
		)
		validated, _, _ = await self._generate_validated(self._build_messages(user_msg))
		return self.make_result(validated)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)



