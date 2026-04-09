from __future__ import annotations

import pytest

from src.agents.launch_strategy.agent import LaunchStrategyAgent
from src.agents.launch_strategy.schemas import LaunchStrategyOutput


@pytest.mark.asyncio
async def test_launch_strategy_agent_validates_schema(monkeypatch) -> None:
	agent = LaunchStrategyAgent()

	class _Text:
		type = "text"

		def __init__(self, text: str) -> None:
			self.text = text

	class _Thinking:
		type = "thinking"

		def __init__(self, thinking: str) -> None:
			self.thinking = thinking

	class _Usage:
		output_tokens = 321

	class _Response:
		def __init__(self, text: str) -> None:
			self.content = [_Thinking("analysis"), _Text(text)]
			self.usage = _Usage()

	def fake_create(**kwargs):  # noqa: ANN003
		_ = kwargs
		return _Response(
			"""```json
			{
			  "positioning_statement": "AI launch intelligence for startup GTM teams",
			  "launch_date_recommendation": "2026-06-01",
			  "phases": [
				{"phase": "Pre-Launch", "duration": "Weeks 1-3", "goals": ["Validate"], "tactics": ["A", "B", "C"], "kpis": ["CTR"]},
				{"phase": "Launch Week", "duration": "Week 4", "goals": ["Convert"], "tactics": ["D", "E", "F"], "kpis": ["Signups"]},
				{"phase": "Post-Launch", "duration": "Weeks 5-8", "goals": ["Retain"], "tactics": ["G", "H", "I"], "kpis": ["Retention"]}
			  ],
			  "channels": ["LinkedIn", "Email"],
			  "budget_allocation": {"content": "40%", "paid": "35%", "community": "25%"},
			  "success_metrics": ["Activation", "CAC"],
			  "risks": ["Limited budget", "Channel saturation"]
			}
			```"""
		)

	monkeypatch.setattr(agent.client.messages, "create", fake_create)
	result = await agent.run(
		{
			"prior_outputs": {
				"market_intelligence": {"white_space": "Fast execution"},
				"audience_insight": {"primary_persona": {"role": "Founder"}},
			}
		}
	)
	parsed = LaunchStrategyOutput(**result.output)
	assert parsed.positioning_statement

