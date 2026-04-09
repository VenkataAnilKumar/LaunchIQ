"""Persona construction helper module."""
from __future__ import annotations

from typing import Any


class PersonaBuilder:
	def build_primary(self, market_data: dict[str, Any]) -> dict[str, Any]:
		positioning = str(market_data.get("recommended_positioning", ""))
		target = "Startup founder / early GTM lead"
		if "product marketer" in positioning.lower():
			target = "Product marketer at growth-stage startup"

		return {
			"name": "Primary ICP Persona",
			"role": target,
			"age_range": "28-42",
			"pain_points": [
				"Slow launch planning cycles",
				"Unclear market differentiation",
			],
			"goals": [
				"Ship launches faster",
				"Improve message-market fit",
			],
			"channels": ["LinkedIn", "Communities", "Email"],
			"message_hook": "Launch with confidence using real market signals",
			"willingness_to_pay": "Medium to high if ROI is measurable",
		}

	def build_secondary(
		self,
		market_data: dict[str, Any],
		primary: dict[str, Any],
	) -> list[dict[str, Any]]:
		_ = market_data
		return [
			{
				"name": "Execution-Focused PMM",
				"role": "Product marketer",
				"age_range": "25-38",
				"pain_points": [
					"Too many channels with limited bandwidth",
					"Difficulty tailoring message by segment",
				],
				"goals": [
					"Increase campaign conversion",
					"Align messaging with personas",
				],
				"channels": ["LinkedIn", "X", "Email"],
				"message_hook": "Turn research into launch-ready messaging in minutes",
				"willingness_to_pay": "Moderate with team-wide adoption",
			}
		]

