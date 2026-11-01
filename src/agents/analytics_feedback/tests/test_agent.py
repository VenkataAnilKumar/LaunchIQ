from __future__ import annotations

import pytest

from src.agents._base.llm import AgentError
from src.agents.analytics_feedback.agent import AnalyticsFeedbackAgent
from src.agents.analytics_feedback.schemas import AnalyticsOutput

METRICS = {"sessions": 1200, "conversions": 48, "engagement_rate": 0.52, "ad_ctr": {"a": 0.031, "b": 0.012}}


@pytest.mark.asyncio
async def test_analytics_agent_validates_with_supplied_metrics() -> None:
	result = await AnalyticsFeedbackAgent().run(
		{"product_name": "Zephyr", "metrics": METRICS, "prior_outputs": {"content_generation": {}}}
	)
	parsed = AnalyticsOutput(**result.output)
	assert 0.0 <= parsed.engagement_score <= 1.0
	assert len(parsed.recommendations) >= 3
	assert result.tokens_used > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{}, {"metrics": {}}, {"metrics": "lots"}, {"ga4_property_id": "properties/1"}])
async def test_analytics_agent_refuses_to_invent_numbers(payload) -> None:
	with pytest.raises(AgentError, match="measured results"):
		await AnalyticsFeedbackAgent().run(payload)
