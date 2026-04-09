"""Analytics & Feedback worker agent."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent

from .anomaly_detector import AnomalyDetector
from .metrics_aggregator import MetricsAggregator
from .recommendation_engine import RecommendationEngine
from .schemas import AnalyticsOutput

GA4_TOOL = {
	"name": "ga4_get_metrics",
	"description": "Fetch Google Analytics 4 metrics for a property",
	"input_schema": {
		"type": "object",
		"properties": {
			"property_id": {"type": "string"},
			"metrics": {"type": "array", "items": {"type": "string"}},
			"dimensions": {"type": "array", "items": {"type": "string"}},
			"date_range": {
				"type": "object",
				"properties": {
					"start_date": {"type": "string"},
					"end_date": {"type": "string"},
				},
			},
		},
		"required": ["property_id", "metrics"],
	},
}


def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class GA4ToolExecutor:
	async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
		if tool_name != "ga4_get_metrics":
			raise ValueError(f"Unknown tool {tool_name}")

		# Phase-4 fallback executor shape; real GA4 integration lands in Phase 5.
		return {
			"property_id": inputs.get("property_id"),
			"metrics": {
				"sessions": 1200,
				"conversions": 48,
				"engagement_rate": 0.52,
			},
		}


class AnalyticsFeedbackAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="analytics_feedback",
				model="claude-haiku-4-5-20251001",
				tools=[GA4_TOOL],
				system_prompt=_load_prompt("system.md"),
			)
		)
		self._aggregator = MetricsAggregator()
		self._anomaly = AnomalyDetector()
		self._recommend = RecommendationEngine()

	def get_output_schema(self) -> type[BaseModel]:
		return AnalyticsOutput

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		ga4_property_id = payload.get("ga4_property_id")
		prior = payload.get("prior_outputs", {}) or {}
		content = prior.get("content_generation", {})

		if ga4_property_id:
			user_msg = (
				"Analyze launch performance with GA4 metrics and return strict JSON. "
				f"property_id={ga4_property_id}."
			)
			messages = self._build_messages(user_msg)
			final_text, tool_calls, _ = await self._call_with_tools(messages, GA4ToolExecutor())

			# If model response fails parsing, fall back to deterministic output from helpers.
			try:
				output_dict = self._extract_json(final_text)
			except Exception:
				metrics = self._aggregator.aggregate({"metrics": {"sessions": 1200, "conversions": 48, "engagement_rate": 0.52}})
				output_dict = self._fallback_output(metrics, content)

			validated = self._validate_output(output_dict)
			return AgentResult(agent_id=self.config.agent_id, output=validated, tool_calls=tool_calls)

		# No GA4: derive insights from available content context.
		metrics = {"sessions": 0.0, "conversions": 0.0, "engagement_rate": 0.45, "conversion_rate": 0.03}
		output_dict = self._fallback_output(metrics, content)
		validated = self._validate_output(output_dict)
		return AgentResult(agent_id=self.config.agent_id, output=validated)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)

	def _fallback_output(self, metrics: dict[str, Any], content: dict[str, Any]) -> dict[str, Any]:
		anomalies = self._anomaly.detect(metrics)
		recs = self._recommend.generate(metrics, content)
		return {
			"engagement_score": float(metrics.get("engagement_rate", 0.0) or 0.0),
			"top_performing_content": ["LinkedIn thought-leadership post", "Awareness email"],
			"underperforming_content": ["Low-CTR ad variant" if anomalies else "None"],
			"recommendations": recs,
			"predicted_next_action": "Optimize onboarding funnel and retest paid copy",
		}

	def _extract_json(self, text: str) -> dict[str, Any]:
		fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		raw = fenced.group(1) if fenced else text.strip()
		if not raw.startswith("{"):
			match = re.search(r"(\{.*\})", raw, re.DOTALL)
			if match:
				raw = match.group(1)
		return json.loads(raw)

