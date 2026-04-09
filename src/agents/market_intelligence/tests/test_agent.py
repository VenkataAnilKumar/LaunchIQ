from __future__ import annotations

import pytest

from src.agents.market_intelligence.agent import MarketIntelligenceAgent
from src.agents.market_intelligence.schemas import MarketIntelligenceOutput


@pytest.mark.asyncio
async def test_agent_validates_schema(monkeypatch) -> None:
		agent = MarketIntelligenceAgent()

		async def fake_call(messages, tool_executor):  # noqa: ANN001
				_ = messages
				_ = tool_executor
				text = """```json
				{
					"market_size": "$4.2B",
					"growth_rate": "18% YoY",
					"competitors": [
						{
							"name": "ProductBoard",
							"positioning": "Roadmap platform",
							"strengths": ["Brand", "Enterprise reach"],
							"weaknesses": ["Complexity", "Cost"],
							"pricing": null
						}
					],
					"trends": [
						{
							"trend": "AI-assisted GTM planning",
							"relevance": "Higher launch velocity",
							"source": "Example Source"
						}
					],
					"white_space": "Fast launch workflows for early-stage teams",
					"recommended_positioning": "AI launch copilot for Seed-Series A SaaS"
				}
				```"""
				return text, [], None

		monkeypatch.setattr(agent, "_call_with_tools", fake_call)
		result = await agent.run(
				{
						"product_name": "LaunchIQ",
						"description": "AI-powered launch intelligence",
						"target_market": "B2B SaaS founders",
						"competitors": ["ProductBoard", "Wynter"],
				}
		)

		parsed = MarketIntelligenceOutput(**result.output)
		assert parsed.market_size
		assert len(parsed.competitors) >= 1

