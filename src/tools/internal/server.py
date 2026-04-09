"""Internal MCP server tool definitions."""
from __future__ import annotations

INTERNAL_TOOLS = [
    {
        "name": "get_prior_output",
        "description": "Get previously saved output for an agent in a launch.",
        "input_schema": {
            "type": "object",
            "properties": {
                "launch_id": {"type": "string"},
                "agent_id": {"type": "string"},
            },
            "required": ["launch_id", "agent_id"],
        },
    },
    {
        "name": "save_output",
        "description": "Persist output for a given launch agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "launch_id": {"type": "string"},
                "agent_id": {"type": "string"},
                "output": {"type": "object"},
            },
            "required": ["launch_id", "agent_id", "output"],
        },
    },
    {
        "name": "get_brief",
        "description": "Retrieve the launch brief for a launch_id.",
        "input_schema": {
            "type": "object",
            "properties": {"launch_id": {"type": "string"}},
            "required": ["launch_id"],
        },
    },
    {
        "name": "get_session_data",
        "description": "Read short-term session data from Redis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "launch_id": {"type": "string"},
                "key": {"type": "string"},
            },
            "required": ["launch_id", "key"],
        },
    },
    {
        "name": "set_session_data",
        "description": "Write short-term session data to Redis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "launch_id": {"type": "string"},
                "key": {"type": "string"},
                "value": {"type": "object"},
            },
            "required": ["launch_id", "key", "value"],
        },
    },
]
