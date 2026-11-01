"""Synthesizer — merges the four agent outputs into one launch brief."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _bullets(items: list[Any] | None) -> str:
	return "\n".join(f"- {i}" for i in (items or [])) or "- (none)"


def to_markdown(brief: dict[str, Any], outputs: dict[str, Any]) -> str:
	"""Render the final launch brief as Markdown (the exportable document)."""
	market = outputs.get("market_intelligence", {}) or {}
	audience = outputs.get("audience_insight", {}) or {}
	strategy = outputs.get("launch_strategy", {}) or {}
	content = outputs.get("content_generation", {}) or {}

	lines = [f"# Launch Brief: {brief.get('product_name', 'Untitled')}", ""]
	lines += [
		f"**Target market:** {brief.get('target_market', '')}",
		"",
		brief.get("description", ""),
		"",
		"## Market Intelligence",
		f"- Market size: {market.get('market_size', 'n/a')}",
		f"- Growth: {market.get('growth_rate', 'n/a')}",
		f"- White space: {market.get('white_space', 'n/a')}",
		f"- Recommended positioning: {market.get('recommended_positioning', 'n/a')}",
		"",
		"### Competitors",
	]
	for c in market.get("competitors", []):
		lines.append(f"- **{c.get('name')}** — {c.get('positioning')} (pricing: {c.get('pricing') or 'n/a'})")
	lines += ["", "### Trends"]
	for t in market.get("trends", []):
		src = f" ([source]({t['source']}))" if t.get("source") else ""
		lines.append(f"- {t.get('trend')} — {t.get('relevance')}{src}")

	lines += ["", "## Audience", audience.get("icp_summary", "")]
	primary = audience.get("primary_persona")
	personas = ([primary] if primary else []) + list(audience.get("secondary_personas", []))
	for p in personas:
		lines += [
			"",
			f"### {p.get('name')} — {p.get('role')}",
			f"Hook: _{p.get('message_hook')}_",
			"Pain points:",
			_bullets(p.get("pain_points")),
			"Goals:",
			_bullets(p.get("goals")),
		]

	lines += ["", "## Launch Strategy", strategy.get("positioning_statement", ""), ""]
	lines.append(f"Recommended launch date: {strategy.get('launch_date_recommendation', 'n/a')}")
	for ph in strategy.get("phases", []):
		lines += ["", f"### {ph.get('phase')} ({ph.get('duration')})", "Tactics:", _bullets(ph.get("tactics")), "KPIs:", _bullets(ph.get("kpis"))]
	lines += ["", "### Budget allocation"]
	for k, v in (strategy.get("budget_allocation") or {}).items():
		lines.append(f"- {k}: {v}")
	lines += ["", "### Risks", _bullets(strategy.get("risks"))]

	lines += ["", "## Content"]
	for section, key in (("Email sequence", "email_sequence"), ("Social posts", "social_posts"), ("Ad copy", "ad_copy")):
		lines += ["", f"### {section}"]
		for item in content.get(key, []):
			lines += [f"**[{item.get('format')} / variant {item.get('variant')}] {item.get('headline')}**", item.get("body", ""), f"CTA: {item.get('cta')}", ""]
	return "\n".join(lines).rstrip() + "\n"


def build_brief(outputs: dict[str, Any]) -> dict[str, Any]:
	"""The four sections the UI renders, assembled from whatever agents have finished."""
	audience = outputs.get("audience_insight") or {}
	personas: list[Any] = []
	if audience.get("primary_persona"):
		personas = [audience["primary_persona"], *audience.get("secondary_personas", [])]
	brief: dict[str, Any] = {}
	if outputs.get("market_intelligence"):
		brief["market_data"] = outputs["market_intelligence"]
	if personas:
		brief["personas"] = personas
	if outputs.get("launch_strategy"):
		brief["strategy"] = outputs["launch_strategy"]
	if outputs.get("content_generation"):
		brief["content"] = outputs["content_generation"]
	return brief


def synthesize(brief: dict[str, Any], outputs: dict[str, Any], usage: dict[str, Any] | None = None) -> dict[str, Any]:
	"""Merge per-agent outputs into the single launch-brief document."""
	strategy = outputs.get("launch_strategy", {}) or {}
	audience = outputs.get("audience_insight", {}) or {}
	return {
		"product_name": brief.get("product_name"),
		"generated_at": datetime.now(UTC).isoformat(),
		"summary": {
			"positioning": strategy.get("positioning_statement"),
			"icp": audience.get("icp_summary"),
			"launch_date_recommendation": strategy.get("launch_date_recommendation"),
		},
		**build_brief(outputs),
		"usage": usage or {},
		"markdown": to_markdown(brief, outputs),
	}
