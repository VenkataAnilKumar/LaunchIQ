"""Unit tests for optional reflection pass and token accounting in CognitiveLoop."""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_reflection_accumulates_tokens_and_returns_refined_text():
    """When enabled, reflection call runs, tokens are added, and refined text is returned."""
    mock_client = MagicMock()

    # First call: end_turn with original text
    resp1 = MagicMock()
    resp1.stop_reason = "end_turn"
    resp1.content = [MagicMock(type="text", text="Original strategy draft.")]
    resp1.usage = MagicMock(input_tokens=100, output_tokens=50)

    # Reflection call
    resp2 = MagicMock()
    resp2.stop_reason = "end_turn"
    resp2.content = [MagicMock(type="text", text="Improved strategy draft with better grounding.")]
    resp2.usage = MagicMock(input_tokens=80, output_tokens=40)

    mock_client.messages.create.side_effect = [resp1, resp2]

    params = {"messages": [{"role": "user", "content": "plan"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(enable_reflection=True, cost_budget_usd=None)

    text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=None, config=cfg)

    assert "Improved strategy" in text
    assert tools == []
    assert mock_client.messages.create.call_count == 2
    assert cfg.total_input_tokens == 180
    assert cfg.total_output_tokens == 90


@pytest.mark.asyncio
async def test_reflection_respects_budget_and_keeps_original_on_breach(caplog):
    """If reflection would exceed budget, original text is kept and warning is logged."""
    mock_client = MagicMock()

    resp1 = MagicMock()
    resp1.stop_reason = "end_turn"
    resp1.content = [MagicMock(type="text", text="Original.")]
    resp1.usage = MagicMock(input_tokens=100_000, output_tokens=20_000)

    resp2 = MagicMock()
    resp2.stop_reason = "end_turn"
    resp2.content = [MagicMock(type="text", text="Refined but expensive.")]
    resp2.usage = MagicMock(input_tokens=50_000, output_tokens=10_000)

    mock_client.messages.create.side_effect = [resp1, resp2]

    params = {"messages": [], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(enable_reflection=True, cost_budget_usd=0.50)

    with caplog.at_level("WARNING"):
        text, _, _ = await run_tool_loop(mock_client, params, None, config=cfg)

    assert text == "Original."
    assert any("reflection" in rec.message.lower() or "budget" in rec.message.lower() for rec in caplog.records)
