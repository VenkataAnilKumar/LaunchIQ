"""Source grounding: trend URLs must come from real search results."""
from __future__ import annotations

import pytest

from src.agents.market_intelligence.agent import MarketIntelligenceAgent, ground_sources

CALLS = [{"tool_name": "tavily_search", "output": {"results": [{"url": "https://real.example/a"}, {"url": "https://real.example/b."}]}}]


def test_unseen_urls_are_nulled_and_seen_urls_kept() -> None:
	out = {"trends": [{"trend": "t1", "source": "https://real.example/a"}, {"trend": "t2", "source": "https://invented.example/x"}, {"trend": "t3", "source": None}]}
	grounded = ground_sources(out, CALLS)
	assert [t["source"] for t in grounded["trends"]] == ["https://real.example/a", None, None]


def test_no_tool_calls_means_no_sources_survive() -> None:
	out = {"trends": [{"trend": "t", "source": "https://anything.example"}]}
	assert ground_sources(out, [])["trends"][0]["source"] is None


@pytest.mark.asyncio
async def test_agent_output_only_cites_urls_it_searched() -> None:
	result = await MarketIntelligenceAgent().run(
		{"product_name": "Zephyr", "description": "d", "target_market": "m", "competitors": ["Acme"]}
	)
	searched = {r["url"] for c in result.tool_calls for r in c["output"]["results"]}
	cited = [t["source"] for t in result.output["trends"] if t["source"]]
	assert cited and set(cited) <= searched
	assert result.tokens_used > 0 and result.cost_usd > 0
