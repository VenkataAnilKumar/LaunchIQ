from __future__ import annotations

import pytest

from src.tools.tavily_search.tools import TavilySearchExecutor


@pytest.mark.asyncio
async def test_tavily_search_passes_query(monkeypatch) -> None:
    executor = TavilySearchExecutor()

    async def fake_search(query: str, max_results: int, search_depth: str) -> dict:
        assert query == "launch intelligence market size"
        assert max_results == 3
        assert search_depth == "advanced"
        return {
            "query": query,
            "answer": "ok",
            "results": [{"title": "source", "content": "snippet"}],
        }

    monkeypatch.setattr(executor, "_search", fake_search)
    result = await executor.execute(
        "tavily_search",
        {
            "query": "launch intelligence market size",
            "max_results": 3,
            "search_depth": "advanced",
        },
    )
    assert result["query"] == "launch intelligence market size"
    assert result["results"]