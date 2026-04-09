"""Lambda-style handler for Content Generation agent."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from .agent import ContentGenerationAgent


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa: ARG001
	payload = event.get("payload", event)
	result = asyncio.run(ContentGenerationAgent().run(payload))
	return {
		"statusCode": 200,
		"body": json.dumps(result.output),
	}

