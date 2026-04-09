"""Lambda-style handler for Market Intelligence agent."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from .agent import MarketIntelligenceAgent


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa: ARG001
	payload = event.get("payload", event)
	result = asyncio.run(MarketIntelligenceAgent().run(payload))
	return {
		"statusCode": 200,
		"body": json.dumps(result.output),
	}

