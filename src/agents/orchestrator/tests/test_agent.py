"""Orchestrator tests: resumable, event-driven pipeline against an in-memory RunStore."""
from __future__ import annotations

from typing import Any

import pytest

from src.agents._base.base_agent import AgentResult
from src.agents.orchestrator.agent import OrchestratorAgent
from src.agents.orchestrator.run_store import MemoryRunStore


class FakeSession:
	def __init__(self) -> None:
		self.events: list[dict[str, Any]] = []

	async def publish(self, channel: str, event: dict[str, Any]) -> None:
		self.events.append(event)


class FakeDispatcher:
	def __init__(self, fail: dict[str, int] | None = None, cost: float = 0.01) -> None:
		self.calls: list[str] = []
		self.payloads: dict[str, dict[str, Any]] = {}
		self.fail = dict(fail or {})
		self.cost = cost

	async def dispatch_result(self, agent_id: str, payload: dict[str, Any]) -> AgentResult:
		self.calls.append(agent_id)
		self.payloads[agent_id] = payload
		if self.fail.get(agent_id, 0) > 0:
			self.fail[agent_id] -= 1
			raise RuntimeError(f"{agent_id} boom")
		return AgentResult(agent_id=agent_id, output={"agent": agent_id}, tokens_used=10, cost_usd=self.cost)


def make(dispatcher: FakeDispatcher | None = None):
	store = MemoryRunStore()
	session = FakeSession()
	disp = dispatcher or FakeDispatcher()
	agent = OrchestratorAgent(store=store, dispatcher=disp, session_store=session)  # type: ignore[arg-type]
	return agent, store, disp, session


PAYLOAD = {"launch_id": "L1", "product_name": "Zephyr", "description": "d", "target_market": "m"}


@pytest.mark.asyncio
async def test_pauses_at_first_checkpoint_and_returns() -> None:
	agent, store, disp, session = make()
	result = await agent.run(PAYLOAD)

	assert result.output["status"] == "hitl_pending"
	assert result.hitl_required and result.hitl_checkpoint == "brief_review"
	assert disp.calls == ["market_intelligence"]
	assert store.launch_status["L1"] == "hitl_pending"
	assert store.checkpoints[("L1", "brief_review")]["decision"] is None
	assert any(e["type"] == "hitl_required" for e in session.events)


@pytest.mark.asyncio
async def test_resume_while_unresolved_does_not_rerun_or_advance() -> None:
	agent, store, disp, _ = make()
	await agent.run(PAYLOAD)
	again = await agent.run(PAYLOAD)
	assert again.output["status"] == "hitl_pending"
	assert disp.calls == ["market_intelligence"]
	assert len([k for k in store.checkpoints]) == 1


@pytest.mark.asyncio
async def test_full_flow_each_agent_runs_exactly_once() -> None:
	agent, store, disp, session = make()
	await agent.run(PAYLOAD)
	store.resolve("L1", "brief_review", "approve")
	second = await agent.run(PAYLOAD)
	assert second.output["status"] == "hitl_pending"
	assert second.hitl_checkpoint == "strategy_review"
	store.resolve("L1", "strategy_review", "approve")
	final = await agent.run(PAYLOAD)

	assert final.output["status"] == "completed"
	assert disp.calls == ["market_intelligence", "audience_insight", "launch_strategy", "content_generation"]
	assert store.launch_status["L1"] == "completed"
	assert "markdown" in store.final_output["L1"]
	assert final.output["cost_usd"] == pytest.approx(0.04)
	assert any(e["type"] == "launch_completed" for e in session.events)


@pytest.mark.asyncio
async def test_downstream_agents_receive_prior_outputs() -> None:
	agent, store, disp, _ = make()
	await agent.run(PAYLOAD)
	store.resolve("L1", "brief_review", "approve")
	await agent.run(PAYLOAD)
	assert disp.payloads["audience_insight"]["prior_outputs"] == {"market_intelligence": {"agent": "market_intelligence"}}


@pytest.mark.asyncio
async def test_reject_halts_pipeline() -> None:
	agent, store, disp, _session = make()
	await agent.run(PAYLOAD)
	store.resolve("L1", "brief_review", "reject")
	result = await agent.run(PAYLOAD)
	assert result.output["status"] == "rejected"
	assert disp.calls == ["market_intelligence"]
	assert store.launch_status["L1"] == "rejected"


@pytest.mark.asyncio
async def test_agent_is_retried_once_then_succeeds() -> None:
	disp = FakeDispatcher(fail={"market_intelligence": 1})
	agent, _store, _, _ = make(disp)
	result = await agent.run(PAYLOAD)
	assert result.output["status"] == "hitl_pending"
	assert disp.calls.count("market_intelligence") == 2


@pytest.mark.asyncio
async def test_agent_failure_is_recorded_and_resume_reruns_only_failed_agent() -> None:
	disp = FakeDispatcher(fail={"audience_insight": 2})
	agent, store, _, session = make(disp)
	await agent.run(PAYLOAD)
	store.resolve("L1", "brief_review", "approve")
	failed = await agent.run(PAYLOAD)

	assert failed.output["status"] == "failed"
	assert "audience_insight" in failed.output["failure_reason"]
	assert store.agents[("L1", "audience_insight")]["status"] == "failed"
	assert any(e["type"] == "agent_failed" for e in session.events)

	disp.calls.clear()
	retried = await agent.run(PAYLOAD)  # e.g. user pressed "retry"
	assert retried.output["status"] == "hitl_pending"
	assert disp.calls == ["audience_insight", "launch_strategy"]


@pytest.mark.asyncio
async def test_cost_budget_stops_pipeline(monkeypatch) -> None:
	monkeypatch.setenv("LAUNCH_COST_BUDGET_USD", "0.015")
	from src.apps.api.config import get_settings

	get_settings.cache_clear()
	try:
		agent, store, disp, _ = make(FakeDispatcher(cost=0.02))
		await agent.run(PAYLOAD)
		store.resolve("L1", "brief_review", "approve")
		result = await agent.run(PAYLOAD)
		assert result.output["status"] == "failed"
		assert "budget" in result.output["failure_reason"]
		assert disp.calls == ["market_intelligence"]
	finally:
		get_settings.cache_clear()


@pytest.mark.asyncio
async def test_requires_launch_id() -> None:
	agent, *_ = make()
	with pytest.raises(ValueError):
		await agent.run({})
