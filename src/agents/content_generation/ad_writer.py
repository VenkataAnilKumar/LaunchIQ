"""Ad-copy-specific content wrapper."""
from __future__ import annotations

from typing import Any


class AdWriter:
	async def write(self, agent: Any, strategy: dict[str, Any], personas: dict[str, Any]) -> list[dict]:
		return await agent._generate_ad_copy(strategy, personas)

