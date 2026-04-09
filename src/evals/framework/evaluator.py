from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.evals.framework.langfuse_client import LangfuseClient
from src.evals.framework.reporter import Reporter
from src.evals.framework.scorer import Scorer


class Evaluator:
	def __init__(self, *, offline: bool = False) -> None:
		self.scorer = Scorer()
		self.langfuse = LangfuseClient()
		self.reporter = Reporter()
		self.offline = offline

	async def run_suite(
		self,
		agent_id: str,
		test_cases: list[dict[str, Any]],
		expected: list[dict[str, Any]],
	) -> dict[str, Any]:
		results: list[dict[str, Any]] = []
		schema_class = self._schema_for_agent(agent_id)

		for index, case in enumerate(test_cases):
			expected_output = expected[index] if index < len(expected) else {}
			inputs = case.get("input", {})
			actual = await self._run_agent(agent_id, inputs)

			scores = self.scorer.score(
				actual,
				expected_output,
				context=inputs,
				schema_class=schema_class,
			)

			case_result = {
				"case_id": case.get("id", f"case_{index + 1}"),
				"input": case,
				"actual": actual,
				"scores": scores,
			}
			results.append(case_result)
			self.langfuse.log(agent_id, case, actual, scores)

		summary = self.reporter.summarize(agent_id, results)
		summary["results"] = results
		return summary

	async def _run_agent(self, agent_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
		if self.offline:
			return self._mock_agent_output(agent_id, inputs)

		from src.agents.orchestrator.dispatcher import AgentDispatcher

		dispatcher = AgentDispatcher()
		try:
			return await dispatcher.dispatch(agent_id, inputs)
		except Exception as exc:
			# Keep regression command stable even if a live model call fails.
			return {
				"_error": str(exc),
				"_agent_id": agent_id,
			}

	def _mock_agent_output(self, agent_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
		product_name = str(inputs.get("product_name", "Product"))

		if agent_id == "market_intelligence":
			return {
				"market_size": "Estimated TAM in low single-digit billions with room for mid-market expansion",
				"growth_rate": "Category growth is strong with double-digit YoY demand",
				"competitors": [
					{
						"name": "Incumbent A",
						"positioning": "Broad suite with enterprise focus",
						"strengths": ["Brand trust", "Wide integrations"],
						"weaknesses": ["Slow onboarding", "High complexity"],
						"pricing": "Premium annual contracts",
					}
				],
				"trends": [
					{
						"trend": "Shift toward AI-assisted execution workflows",
						"relevance": "Directly increases willingness to trial faster automation",
						"source": "Synthetic offline fixture",
					}
				],
				"white_space": "Simple guided workflow for teams that need speed over configurability",
				"recommended_positioning": f"{product_name} as the fastest path from strategy to launch assets",
			}

		if agent_id == "audience_insight":
			return {
				"primary_persona": {
					"name": "Growth-focused Product Marketer",
					"role": "Product Marketing Manager",
					"age_range": "28-40",
					"pain_points": [
						"Too much manual research before launch",
						"Hard to align cross-functional messaging quickly",
					],
					"goals": [
						"Reduce time-to-launch",
						"Improve campaign confidence with better insight",
					],
					"channels": ["LinkedIn", "Email", "Product communities"],
					"message_hook": "Plan launches in hours, not weeks, with AI-guided execution.",
					"willingness_to_pay": "Mid to high for measurable speed gains",
				},
				"secondary_personas": [
					{
						"name": "Founder-Operator",
						"role": "Startup Founder",
						"age_range": "25-45",
						"pain_points": ["Small team bandwidth", "Unclear GTM priorities"],
						"goals": ["Faster launch cycles", "Better market learning"],
						"channels": ["X", "Founder newsletters"],
						"message_hook": "Ship confident launches without building a full marketing org.",
						"willingness_to_pay": "Value-based if outcomes are visible",
					}
				],
				"icp_summary": "Lean SaaS teams shipping frequent product updates with limited GTM bandwidth.",
				"messaging_framework": {
					"awareness": "Missed launch opportunities due to fragmented planning",
					"consideration": "Structured AI workflow to unify research, strategy, and content",
					"decision": "Demonstrated reduction in planning and execution cycle time",
				},
				"recommended_channels": ["LinkedIn", "Lifecycle email", "Webinars"],
			}

		if agent_id == "launch_strategy":
			return {
				"positioning_statement": f"{product_name} helps modern teams move from insight to launch execution with less friction.",
				"launch_date_recommendation": "Target a Tuesday product announcement with 2-week prelaunch warmup",
				"phases": [
					{
						"phase": "Pre-Launch",
						"duration": "2 weeks",
						"goals": ["Build pipeline", "Validate messaging resonance"],
						"tactics": ["Landing page waitlist", "Founder narrative post", "Targeted email teaser"],
						"kpis": ["Waitlist signups", "CTR", "Reply rate"],
					},
					{
						"phase": "Launch Week",
						"duration": "1 week",
						"goals": ["Drive awareness spike", "Convert qualified demand"],
						"tactics": ["Launch announcement", "Demo webinar", "Partner amplification"],
						"kpis": ["Site sessions", "Demo bookings", "Trials started"],
					},
					{
						"phase": "Post-Launch",
						"duration": "2 weeks",
						"goals": ["Sustain demand", "Capture feedback loops"],
						"tactics": ["Customer stories", "Objection-handling content", "Retargeting ads"],
						"kpis": ["Activation rate", "CAC", "Pipeline influenced"],
					},
				],
				"channels": ["LinkedIn", "Email", "Webinars", "Community channels"],
				"budget_allocation": {
					"paid": "35%",
					"content": "25%",
					"events": "20%",
					"experiments": "20%",
				},
				"success_metrics": ["Qualified pipeline", "Activation", "Cost per activated account"],
				"risks": ["Message dilution", "Underpowered follow-up sequences"],
			}

		if agent_id == "content_generation":
			return {
				"email_sequence": [
					{
						"format": "email",
						"variant": "a",
						"headline": f"Launch faster with {product_name}",
						"body": "Turn weeks of launch planning into an actionable plan in one guided workflow.",
						"cta": "Book a demo",
						"target_persona": "Product marketer",
					},
					{
						"format": "email",
						"variant": "b",
						"headline": "From research to campaign execution in one day",
						"body": "Unify market intel, audience insight, and messaging in a single launch workspace.",
						"cta": "Start trial",
						"target_persona": "Founder",
					},
					{
						"format": "email",
						"variant": "a",
						"headline": "Ship launches with confidence",
						"body": "Use structured AI outputs and HITL checkpoints to keep quality high.",
						"cta": "See workflow",
						"target_persona": "Growth lead",
					},
				],
				"social_posts": [
					{
						"format": "linkedin",
						"variant": "a",
						"headline": "Launch planning is broken",
						"body": "Most teams spend weeks stitching strategy docs. We replaced that with one guided AI workflow.",
						"cta": "Learn more",
						"target_persona": "Product marketer",
					},
					{
						"format": "twitter",
						"variant": "b",
						"headline": "Ship smarter launches",
						"body": "Research, positioning, and content in one loop. Less prep, better execution.",
						"cta": "Try it",
						"target_persona": "Founder",
					},
					{
						"format": "linkedin",
						"variant": "a",
						"headline": "Your AI launch team",
						"body": "Turn product inputs into a full go-to-market playbook in minutes.",
						"cta": "Book demo",
						"target_persona": "Growth lead",
					},
				],
				"ad_copy": [
					{
						"format": "ad_copy",
						"variant": "a",
						"headline": "Launch in days, not weeks",
						"body": "Structured AI strategy and content for modern product teams.",
						"cta": "Start free",
						"target_persona": "Product marketer",
					},
					{
						"format": "ad_copy",
						"variant": "b",
						"headline": "Better GTM execution",
						"body": "Discover, decide, and deploy with AI-assisted launch workflows.",
						"cta": "Request demo",
						"target_persona": "Founder",
					},
				],
				"brand_voice_notes": "Confident, practical, and outcome-oriented with clear next steps.",
			}

		return {"_error": f"Unsupported offline agent: {agent_id}", "_agent_id": agent_id}

	def _schema_for_agent(self, agent_id: str) -> type[BaseModel] | None:
		mapping: dict[str, str] = {
			"market_intelligence": "src.agents.market_intelligence.schemas.MarketIntelligenceOutput",
			"audience_insight": "src.agents.audience_insight.schemas.AudienceInsightOutput",
			"launch_strategy": "src.agents.launch_strategy.schemas.LaunchStrategyOutput",
			"content_generation": "src.agents.content_generation.schemas.ContentBundle",
		}
		path = mapping.get(agent_id)
		if not path:
			return None

		module_path, class_name = path.rsplit(".", 1)
		try:
			module = __import__(module_path, fromlist=[class_name])
			resolved = getattr(module, class_name)
			if isinstance(resolved, type) and issubclass(resolved, BaseModel):
				return resolved
		except Exception:
			return None
		return None
