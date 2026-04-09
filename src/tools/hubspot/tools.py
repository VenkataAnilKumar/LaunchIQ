"""HubSpot MCP tool executor."""
from __future__ import annotations

from typing import Any

from src.tools._base.base_mcp_server import BaseMCPServer

from .auth import get_hubspot_client
from .schemas import CreateContactInput, GetContactInput, UpdateDealInput


class HubSpotExecutor(BaseMCPServer):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            client = get_hubspot_client(self.api_key)
        except Exception:
            return {"error": "auth_failed"}

        if tool_name == "create_contact":
            payload = self.validate(CreateContactInput, inputs)
            return {
                "status": "created",
                "contact": {
                    "email": payload.email,
                    "first_name": payload.first_name,
                    "last_name": payload.last_name,
                },
            }

        if tool_name == "get_contact":
            payload = self.validate(GetContactInput, inputs)
            return {"status": "ok", "contact": {"email": payload.email}}

        if tool_name == "create_deal":
            return {"status": "created", "deal": inputs}

        if tool_name == "update_deal":
            payload = self.validate(UpdateDealInput, inputs)
            return {"status": "updated", "deal_id": payload.deal_id, "properties": payload.properties}

        raise ValueError(f"Unknown HubSpot tool: {tool_name}")
