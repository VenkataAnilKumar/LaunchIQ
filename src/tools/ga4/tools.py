"""GA4 MCP tool executor."""
from __future__ import annotations

from typing import Any

from src.tools._base.base_mcp_server import BaseMCPServer

from .auth import get_ga4_client
from .schemas import GetMetricsInput, MetricsResponse


class GA4Executor(BaseMCPServer):
    def __init__(self, credentials: dict[str, Any] | None = None) -> None:
        self.credentials = credentials or {}

    async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            _client = get_ga4_client(self.credentials)
        except Exception:
            return {"error": "auth_failed"}

        if tool_name == "ga4_get_metrics":
            payload = self.validate(GetMetricsInput, inputs)
            return MetricsResponse(
                property_id=payload.property_id,
                metrics={m: 0.0 for m in payload.metrics},
            ).model_dump()

        if tool_name == "ga4_get_events":
            payload = self.validate(GetMetricsInput, inputs)
            return {"property_id": payload.property_id, "events": []}

        if tool_name == "ga4_get_conversions":
            payload = self.validate(GetMetricsInput, inputs)
            return {"property_id": payload.property_id, "conversions": []}

        raise ValueError(f"Unknown GA4 tool: {tool_name}")
