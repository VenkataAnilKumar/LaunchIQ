from __future__ import annotations

import pytest

from src.agents.content_generation.agent import ContentGenerationAgent
from src.agents.content_generation.schemas import ContentBundle


@pytest.mark.asyncio
async def test_content_generation_agent_validates_bundle(monkeypatch) -> None:
	agent = ContentGenerationAgent()

	async def fake_emails(strategy, personas):  # noqa: ANN001
		_ = strategy
		_ = personas
		return [
			{"format": "email", "variant": "a", "headline": "H1", "body": "B1", "cta": "C1", "target_persona": "Founder"},
			{"format": "email", "variant": "b", "headline": "H2", "body": "B2", "cta": "C2", "target_persona": "Founder"},
			{"format": "email", "variant": "a", "headline": "H3", "body": "B3", "cta": "C3", "target_persona": "PMM"},
		]

	async def fake_social(strategy, personas):  # noqa: ANN001
		_ = strategy
		_ = personas
		return [
			{"format": "linkedin", "variant": "a", "headline": "S1", "body": "SB1", "cta": "SC1", "target_persona": "Founder"},
			{"format": "twitter", "variant": "b", "headline": "S2", "body": "SB2", "cta": "SC2", "target_persona": "PMM"},
			{"format": "linkedin", "variant": "a", "headline": "S3", "body": "SB3", "cta": "SC3", "target_persona": "Founder"},
		]

	async def fake_ads(strategy, personas):  # noqa: ANN001
		_ = strategy
		_ = personas
		return [
			{"format": "ad_copy", "variant": "a", "headline": "A1", "body": "AB1", "cta": "AC1", "target_persona": "Founder"},
			{"format": "ad_copy", "variant": "b", "headline": "A2", "body": "AB2", "cta": "AC2", "target_persona": "PMM"},
		]

	monkeypatch.setattr(agent, "_generate_email_sequence", fake_emails)
	monkeypatch.setattr(agent, "_generate_social_posts", fake_social)
	monkeypatch.setattr(agent, "_generate_ad_copy", fake_ads)

	result = await agent.run({"prior_outputs": {"launch_strategy": {}, "audience_insight": {}}})
	parsed = ContentBundle(**result.output)
	assert len(parsed.email_sequence) >= 3
	assert len(parsed.ad_copy) >= 2

