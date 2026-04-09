from __future__ import annotations

import pytest

from src.agents.audience_insight.agent import AudienceInsightAgent
from src.agents.audience_insight.schemas import AudienceInsightOutput


@pytest.mark.asyncio
async def test_audience_agent_validates_schema(monkeypatch) -> None:
	agent = AudienceInsightAgent()

	class _TextBlock:
		type = "text"

		def __init__(self, text: str) -> None:
			self.text = text

	class _Usage:
		output_tokens = 123

	class _Response:
		def __init__(self, text: str) -> None:
			self.content = [_TextBlock(text)]
			self.usage = _Usage()

	def fake_create(**kwargs):  # noqa: ANN003
		_ = kwargs
		return _Response(
			"""```json
			{
			  "primary_persona": {
				"name": "Sarah Chen",
				"role": "Founder",
				"age_range": "32-40",
				"pain_points": ["Manual launch prep", "Slow iteration"],
				"goals": ["Faster launches", "Clearer positioning"],
				"channels": ["LinkedIn", "Email"],
				"message_hook": "Launch with market-backed confidence",
				"willingness_to_pay": "High"
			  },
			  "secondary_personas": [],
			  "icp_summary": "Early-stage B2B SaaS teams with lean GTM resources",
			  "messaging_framework": {"awareness": "Use market proof", "conversion": "Show speed-to-value"},
			  "recommended_channels": ["LinkedIn", "Email"]
			}
			```"""
		)

	monkeypatch.setattr(agent.client.messages, "create", fake_create)

	result = await agent.run(
		{
			"prior_outputs": {
				"market_intelligence": {
					"recommended_positioning": "AI launch intelligence for startup GTM teams"
				}
			}
		}
	)
	parsed = AudienceInsightOutput(**result.output)
	assert parsed.primary_persona.name == "Sarah Chen"

