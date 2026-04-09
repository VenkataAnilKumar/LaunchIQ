"""GA4 MCP server tool definitions."""
from __future__ import annotations

GA4_TOOLS = [
    {
        "name": "ga4_get_metrics",
        "description": "Fetch GA4 metrics for a property.",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_id": {"type": "string"},
                "metrics": {"type": "array", "items": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}},
                "date_range": {"type": "object"},
            },
            "required": ["property_id", "metrics"],
        },
    },
    {
        "name": "ga4_get_events",
        "description": "Fetch GA4 event rows.",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_id": {"type": "string"},
                "metrics": {"type": "array", "items": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}},
                "date_range": {"type": "object"},
            },
            "required": ["property_id", "metrics"],
        },
    },
    {
        "name": "ga4_get_conversions",
        "description": "Fetch GA4 conversion rows.",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_id": {"type": "string"},
                "metrics": {"type": "array", "items": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}},
                "date_range": {"type": "object"},
            },
            "required": ["property_id", "metrics"],
        },
    },
]
