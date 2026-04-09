from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.agents.orchestrator.agent import OrchestratorAgent


@pytest.mark.asyncio
async def test_run_calls_dispatcher_for_pipeline_agents(monkeypatch) -> None:
	agent = OrchestratorAgent()

	async def fake_dispatch(agent_id: str, payload: dict) -> dict:
		return {"agent": agent_id, "ok": True}

	monkeypatch.setattr(agent.dispatcher, "dispatch", fake_dispatch)
	monkeypatch.setattr(agent, "_pause_for_hitl", AsyncMock())
	monkeypatch.setattr(
		agent,
		"_wait_for_hitl_resolution",
		AsyncMock(return_value={"decision": "approve", "edits": None}),
	)

	result = await agent.run({"launch_id": "launch-1", "product_name": "Test"})
	assert result.output["status"] == "completed"
	assert len(result.output["agent_outputs"]) == 4


@pytest.mark.asyncio
async def test_hitl_pause_and_resume(monkeypatch) -> None:
	agent = OrchestratorAgent()
	monkeypatch.setattr(
		agent.dispatcher,
		"dispatch",
		AsyncMock(return_value={"draft": "initial"}),
	)
	monkeypatch.setattr(agent, "_pause_for_hitl", AsyncMock())
	monkeypatch.setattr(
		agent,
		"_wait_for_hitl_resolution",
		AsyncMock(return_value={"decision": "approve", "edits": {"draft": "edited"}}),
	)

	result = await agent.run({"launch_id": "launch-2", "product_name": "Test"})
	assert result.output["status"] == "completed"

