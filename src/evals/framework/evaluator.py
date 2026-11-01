"""Pipeline evaluator: runs the real agents over the brief corpus and scores each output.

With LLM_PROVIDER=fake (``--offline``) this verifies the plumbing — prompting, parsing,
validation, repair, grounding, orchestration inputs — on every brief, including adversarial
ones, without any API key. It does NOT measure model quality; that needs a live run.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.agents.audience_insight.schemas import AudienceInsightOutput
from src.agents.content_generation.schemas import ContentBundle
from src.agents.launch_strategy.schemas import LaunchStrategyOutput
from src.agents.market_intelligence.schemas import MarketIntelligenceOutput
from src.evals.metrics.grounding import (
	citation_coverage,
	leaked_forbidden_text,
	product_mention,
)
from src.evals.metrics.hallucination import HallucinationScorer
from src.evals.metrics.schema_compliance import SchemaComplianceScorer

CORPUS_PATH = Path(__file__).resolve().parents[1] / "corpus" / "briefs.json"

PIPELINE = ["market_intelligence", "audience_insight", "launch_strategy", "content_generation"]

SCHEMAS: dict[str, type[BaseModel]] = {
	"market_intelligence": MarketIntelligenceOutput,
	"audience_insight": AudienceInsightOutput,
	"launch_strategy": LaunchStrategyOutput,
	"content_generation": ContentBundle,
}

# Metrics where a LOWER value is better (used by the baseline gate).
LOWER_IS_BETTER = {"hallucination_rate", "error_rate", "injection_leak_rate", "cost_usd", "tokens"}


def load_corpus() -> list[dict[str, Any]]:
	return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


class Evaluator:
	def __init__(self) -> None:
		self._schema = SchemaComplianceScorer()
		self._halluc = HallucinationScorer()

	async def run_corpus(
		self, briefs: list[dict[str, Any]] | None = None, agents: list[str] | None = None
	) -> dict[str, dict[str, Any]]:
		from src.agents.orchestrator.dispatcher import AgentDispatcher

		briefs = briefs if briefs is not None else load_corpus()
		wanted = agents or PIPELINE
		dispatcher = AgentDispatcher()
		rows: dict[str, list[dict[str, Any]]] = {a: [] for a in wanted}

		for brief in briefs:
			prior: dict[str, Any] = {}
			for agent_id in PIPELINE:
				if agent_id not in wanted and agent_id not in {a for a in PIPELINE[: PIPELINE.index(wanted[-1]) + 1]}:
					continue
				payload = {k: v for k, v in brief.items() if k not in {"id", "adversarial", "forbidden_text"}}
				payload["launch_id"] = f"eval-{brief['id']}"
				payload["prior_outputs"] = dict(prior)
				try:
					result = await dispatcher.dispatch_result(agent_id, payload)
				except Exception as exc:  # recorded as an error row; never hides failures  # noqa: BLE001 - recorded as an error row
					if agent_id in rows:
						rows[agent_id].append({"brief": brief["id"], "error": f"{type(exc).__name__}: {exc}"})
					break  # downstream agents depend on this output
				prior[agent_id] = result.output
				if agent_id in rows:
					rows[agent_id].append(self._score(agent_id, brief, result.output, result))
		return {agent_id: self._summarize(agent_id, r) for agent_id, r in rows.items()}

	def _score(self, agent_id: str, brief: dict[str, Any], output: dict[str, Any], result: Any) -> dict[str, Any]:
		scores: dict[str, Any] = {
			"brief": brief["id"],
			"schema_compliance": self._schema.score(output, SCHEMAS[agent_id]),
			"hallucination_rate": self._halluc.score(output, brief),
			"product_mention": product_mention(agent_id, output, brief["product_name"]),
			"tokens": result.tokens_used,
			"cost_usd": result.cost_usd,
		}
		if agent_id == "market_intelligence":
			scores["citation_coverage"] = citation_coverage(output)
		if brief.get("forbidden_text"):
			scores["injection_leak"] = leaked_forbidden_text(output, brief["forbidden_text"])
		return scores

	@staticmethod
	def _summarize(agent_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
		total = len(rows)
		errors = [r for r in rows if "error" in r]
		ok = [r for r in rows if "error" not in r]

		def mean(key: str) -> float | None:
			vals = [float(r[key]) for r in ok if key in r]
			return round(sum(vals) / len(vals), 4) if vals else None

		summary: dict[str, Any] = {
			"agent_id": agent_id,
			"total_cases": total,
			"error_rate": round(len(errors) / total, 4) if total else 1.0,
			"errors": [{"brief": e["brief"], "error": e["error"]} for e in errors],
		}
		for key in ("schema_compliance", "hallucination_rate", "product_mention", "citation_coverage", "tokens", "cost_usd"):
			value = mean(key)
			if value is not None:
				summary[key] = value
		leaks = [r for r in ok if "injection_leak" in r]
		if leaks:
			summary["injection_leak_rate"] = round(sum(1 for r in leaks if r["injection_leak"]) / len(leaks), 4)
		return summary
