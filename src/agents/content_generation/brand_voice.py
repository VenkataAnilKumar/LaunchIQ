"""Brand voice extraction helper."""
from __future__ import annotations

from typing import Any


class BrandVoiceExtractor:
	def extract(self, strategy_output: dict[str, Any]) -> dict[str, str]:
		positioning = str(strategy_output.get("positioning_statement", ""))
		return {
			"tone": "Confident, practical, evidence-driven",
			"vocabulary": "launch velocity, validation, measurable outcomes",
			"key_messages": positioning or "Faster launches with better positioning",
		}

