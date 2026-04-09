"""Segment-to-message mapping helper."""
from __future__ import annotations


class SegmentMapper:
	def map_segments(self, personas: list[dict]) -> dict[str, str]:
		mapping: dict[str, str] = {}
		for persona in personas:
			name = str(persona.get("name", "Unknown"))
			role = str(persona.get("role", "buyer"))
			mapping[name] = f"For {role}: launch faster with clearer market-backed positioning."
		return mapping

