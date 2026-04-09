"""Tavily MCP tool definitions."""
from __future__ import annotations

from .tools import TavilySearchExecutor

TAVILY_TOOLS = [
	{
		"name": "tavily_search",
		"description": "Search the web for market and competitor intelligence.",
		"input_schema": {
			"type": "object",
			"properties": {
				"query": {"type": "string", "minLength": 3},
				"max_results": {"type": "integer", "minimum": 1, "maximum": 10},
				"search_depth": {"type": "string"},
			},
			"required": ["query"],
		},
	}
]


def get_server() -> TavilySearchExecutor:
	return TavilySearchExecutor()

