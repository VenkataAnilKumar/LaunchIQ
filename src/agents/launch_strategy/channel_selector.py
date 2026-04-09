"""Channel selection helper."""
from __future__ import annotations

from typing import Any


class ChannelSelector:
	def select_channels(self, personas: dict[str, Any], budget: str) -> list[str]:
		_ = budget
		channels = {"LinkedIn", "Email", "Webinars"}
		primary = personas.get("primary_persona", {}) if isinstance(personas, dict) else {}
		for channel in primary.get("channels", []) if isinstance(primary, dict) else []:
			channels.add(str(channel))
		return sorted(channels)

