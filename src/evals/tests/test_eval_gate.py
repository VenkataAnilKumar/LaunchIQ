"""The offline eval gate must pass on the real agents — and must actually be able to fail."""
from __future__ import annotations

import pytest

from src.agents._base import fake_llm
from src.evals.framework.evaluator import Evaluator, load_corpus
from src.evals.regression.run_regression import check_baseline, load_baseline


def test_corpus_covers_diverse_and_adversarial_briefs() -> None:
	corpus = load_corpus()
	assert len(corpus) >= 15
	assert len({b["id"] for b in corpus}) == len(corpus)
	assert sum(1 for b in corpus if b.get("adversarial") == "injection") >= 2
	assert any(not b["competitors"] for b in corpus)


@pytest.mark.asyncio
async def test_offline_gate_passes_for_real_agents() -> None:
	results = await Evaluator().run_corpus()
	assert check_baseline(results, load_baseline("offline")) == []
	assert all(r["total_cases"] == len(load_corpus()) for r in results.values())


@pytest.mark.asyncio
async def test_gate_fails_when_an_agent_breaks(monkeypatch) -> None:
	real = fake_llm._strategy
	monkeypatch.setattr(fake_llm, "_strategy", lambda name: {**real(name), "phases": []})  # violates min_length
	results = await Evaluator().run_corpus()
	failures = check_baseline(results, load_baseline("offline"))
	assert any(f.startswith("launch_strategy.error_rate") for f in failures)
	# downstream of the broken agent is skipped for those briefs, not silently green
	assert results["content_generation"]["total_cases"] == 0


@pytest.mark.asyncio
async def test_gate_catches_prompt_injection_leak(monkeypatch) -> None:
	real = fake_llm._audience
	monkeypatch.setattr(fake_llm, "_audience", lambda: {**real(), "icp_summary": "PWNED and LEAKED"})
	results = await Evaluator().run_corpus()
	failures = check_baseline(results, load_baseline("offline"))
	assert any("injection_leak_rate" in f for f in failures)


@pytest.mark.asyncio
async def test_gate_catches_fabricated_citation(monkeypatch) -> None:
	import src.agents.market_intelligence.agent as mi

	monkeypatch.setattr(mi, "ground_sources", lambda out, calls: out)  # grounding disabled
	real = fake_llm._market
	monkeypatch.setattr(
		fake_llm,
		"_market",
		lambda name, urls=None: {**real(name, urls), "trends": [{"trend": "t", "relevance": "r", "source": None}]},
	)
	results = await Evaluator().run_corpus(agents=["market_intelligence"])
	assert any("citation_coverage" in f for f in check_baseline(results, load_baseline("offline")))
