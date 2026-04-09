"""Slack MCP server tool definitions."""
from __future__ import annotations

SLACK_TOOLS = [
    {
        "name": "post_message",
        "description": "Post a message to a Slack channel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "text": {"type": "string"},
                "blocks": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["channel", "text"],
        },
    },
    {
        "name": "get_channel_info",
        "description": "Get information for a Slack channel.",
        "input_schema": {
            "type": "object",
            "properties": {"channel": {"type": "string"}},
            "required": ["channel"],
        },
    },
    {
        "name": "list_channels",
        "description": "List available Slack channels.",
        "input_schema": {"type": "object", "properties": {}},
    },
]
