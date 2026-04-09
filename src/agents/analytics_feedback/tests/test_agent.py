from __future__ import annotations

import pytest

from src.agents.analytics_feedback.agent import AnalyticsFeedbackAgent
from src.agents.analytics_feedback.schemas import AnalyticsOutput


@pytest.mark.asyncio
async def test_analytics_agent_no_ga4_fallback_validates() -> None:
	agent = AnalyticsFeedbackAgent()
	result = await agent.run({"prior_outputs": {"content_generation": {}}})
	parsed = AnalyticsOutput(**result.output)
	assert 0.0 <= parsed.engagement_score <= 1.0
	assert len(parsed.recommendations) >= 3

