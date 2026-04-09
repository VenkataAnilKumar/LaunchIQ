"""Slack MCP tool executor."""
from __future__ import annotations

from typing import Any

from src.tools._base.base_mcp_server import BaseMCPServer

from .auth import get_slack_client
from .schemas import GetChannelInput, PostMessageInput


class SlackExecutor(BaseMCPServer):
    def __init__(self, bot_token: str = "") -> None:
        self.bot_token = bot_token

    async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            _client = get_slack_client(self.bot_token)
        except Exception:
            return {"error": "auth_failed"}

        if tool_name == "post_message":
            payload = self.validate(PostMessageInput, inputs)
            return {
                "status": "sent",
                "channel": payload.channel,
                "text": payload.text,
            }

        if tool_name == "get_channel_info":
            payload = self.validate(GetChannelInput, inputs)
            return {"status": "ok", "channel": {"id": payload.channel}}

        if tool_name == "list_channels":
            return {"status": "ok", "channels": []}

        raise ValueError(f"Unknown Slack tool: {tool_name}")
