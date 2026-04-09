"""Tavily search tool executor."""
from __future__ import annotations

from typing import Any

import httpx

from src.apps.api.config import get_settings
from src.tools._base.base_mcp_server import BaseMCPServer

from .schemas import TavilySearchInput, TavilySearchResult


class TavilySearchExecutor(BaseMCPServer):
	async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
		if tool_name not in {"tavily_search", "tavily_search_web"}:
			raise ValueError(f"Unknown Tavily tool: {tool_name}")

		payload = self.validate(TavilySearchInput, inputs)
		result = await self._search(payload.query, payload.max_results, payload.search_depth)
		return TavilySearchResult(**result).model_dump()

	async def _search(
		self,
		query: str,
		max_results: int,
		search_depth: str,
	) -> dict[str, Any]:
		settings = get_settings()
		body = {
			"api_key": settings.tavily_api_key,
			"query": query,
			"max_results": max_results,
			"search_depth": search_depth,
		}

		try:
			async with httpx.AsyncClient(timeout=30.0) as client:
				response = await client.post("https://api.tavily.com/search", json=body)
				response.raise_for_status()
				data = response.json()
		except httpx.HTTPStatusError as exc:
			return {"results": [], "answer": None, "query": query, "error": "search_failed", "detail": str(exc)}

		return {
			"results": data.get("results", []),
			"answer": data.get("answer"),
			"query": query,
		}


