"""Additional unit tests for CognitiveLoop cost-budget observability."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_budget_approaching_is_logged(caplog):
    """When estimated cost approaches or exceeds the budget, status appears in logs."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(type="text", text="Done.")]
    # Simulate high token usage that will exceed a small budget
    mock_usage = MagicMock(input_tokens=200_000, output_tokens=50_000)
    mock_response.usage = mock_usage
    mock_client.messages.create.return_value = mock_response

    params = {"messages": [{"role": "user", "content": "test"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(enable_reflection=False, cost_budget_usd=0.10)

    with caplog.at_level("INFO"):
        await run_tool_loop(mock_client, params, tool_executor=None, config=cfg)

    log_text = " ".join(rec.message for rec in caplog.records)
    assert "budget" in log_text.lower() or "cost" in log_text.lower()
    # Structured payload should have been logged
    assert any("estimated_cost_usd" in rec.message or "budget_status" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_budget_approaching_soft_warning_at_80_percent(caplog):
    """Soft INFO warning is emitted when cost exceeds 80% but stays under budget."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(type="text", text="Partial result.")]
    # Tokens that produce ~0.09 USD (under 0.10 budget, over 0.08)
    mock_usage = MagicMock(input_tokens=180_000, output_tokens=40_000)
    mock_response.usage = mock_usage
    mock_client.messages.create.return_value = mock_response

    params = {"messages": [{"role": "user", "content": "test"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(enable_reflection=False, cost_budget_usd=0.10)

    with caplog.at_level("INFO"):
        text, _, _ = await run_tool_loop(mock_client, params, tool_executor=None, config=cfg)

    assert "Partial result." in text
    assert any(
        getattr(rec, "budget_status", None) == "approaching" or "approaching" in rec.message.lower()
        for rec in caplog.records
    )
