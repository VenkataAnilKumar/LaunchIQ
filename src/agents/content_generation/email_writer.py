"""Email-specific content wrapper."""
from __future__ import annotations

from typing import Any


class EmailWriter:
	async def write(self, agent: Any, strategy: dict[str, Any], personas: dict[str, Any]) -> list[dict]:
		return await agent._generate_email_sequence(strategy, personas)

