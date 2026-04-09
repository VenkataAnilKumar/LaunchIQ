"""Messaging hook generation helper."""
from __future__ import annotations


class MessagingGenerator:
	def generate_hooks(self, personas: list[dict]) -> dict[str, str]:
		hooks: dict[str, str] = {}
		for persona in personas:
			name = str(persona.get("name", "Unknown"))
			pain_points = persona.get("pain_points", [])
			top_pain = pain_points[0] if isinstance(pain_points, list) and pain_points else "launch friction"
			hooks[name] = f"Eliminate {top_pain.lower()} with actionable launch intelligence."
		return hooks

