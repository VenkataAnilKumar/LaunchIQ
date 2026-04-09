"""Recommendation generation helper."""
from __future__ import annotations

from typing import Any


class RecommendationEngine:
	def generate(self, metrics: dict[str, Any], content: dict[str, Any]) -> list[dict[str, str]]:
		_ = content
		recs: list[dict[str, str]] = [
			{
				"area": "Onboarding",
				"insight": "Activation is below target in the first session.",
				"action": "Shorten time-to-value with guided setup and a 2-minute checklist.",
				"priority": "high",
			},
			{
				"area": "Messaging",
				"insight": "Conversion may be constrained by unclear differentiation.",
				"action": "Test value-prop variants focused on launch speed and confidence.",
				"priority": "medium",
			},
			{
				"area": "Channels",
				"insight": "Session volume suggests channel mix can be expanded.",
				"action": "Shift 15% budget to the top-performing acquisition channel.",
				"priority": "medium",
			},
		]
		if float(metrics.get("engagement_rate", 0) or 0) >= 0.6:
			recs[1]["priority"] = "low"
		return recs

