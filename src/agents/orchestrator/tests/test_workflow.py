from __future__ import annotations

from src.agents.orchestrator.workflow_state import WorkflowState


def test_workflow_state_mark_complete() -> None:
	state = WorkflowState(launch_id="l1", brief={})
	state.mark_agent_complete("market_intelligence", {"a": 1})
	assert state.agent_outputs["market_intelligence"] == {"a": 1}
	assert state.completed_agents == ["market_intelligence"]


def test_workflow_resume_from_hitl_merges_edits() -> None:
	state = WorkflowState(launch_id="l2", brief={})
	state.mark_agent_complete("launch_strategy", {"plan": "A"})
	state.mark_hitl_pending("strategy_review")
	state.resume_from_hitl({"plan": "B"})
	assert state.agent_outputs["launch_strategy"]["plan"] == "B"
	assert state.hitl_pending is False

