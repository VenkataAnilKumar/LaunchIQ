"""HubSpot MCP server tool definitions."""
from __future__ import annotations

HUBSPOT_TOOLS = [
    {
        "name": "create_contact",
        "description": "Create a HubSpot contact.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "get_contact",
        "description": "Fetch contact by email.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
    },
    {
        "name": "create_deal",
        "description": "Create a HubSpot deal.",
        "input_schema": {"type": "object", "properties": {"properties": {"type": "object"}}, "required": ["properties"]},
    },
    {
        "name": "update_deal",
        "description": "Update a HubSpot deal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "string"},
                "properties": {"type": "object"},
            },
            "required": ["deal_id", "properties"],
        },
    },
]
