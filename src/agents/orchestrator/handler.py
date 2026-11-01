"""Lambda-style handler for orchestrator execution."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from .agent import OrchestratorAgent


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
	payload = event.get("payload", event)
	result = asyncio.run(OrchestratorAgent().run(payload))
	return {
		"statusCode": 200,
		"body": json.dumps(result.output),
	}

