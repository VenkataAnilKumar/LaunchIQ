"""Unit tests for CognitiveLoop completion metric events."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_completion_metric_emitted_on_normal_exit(caplog):
    """Normal end_turn path emits cognitive_loop_completion_event with iterations and tool calls."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(type="text", text="Launch plan ready.")]
    mock_client.messages.create.return_value = mock_response

    params = {"messages": [{"role": "user", "content": "Create strategy"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(enable_reflection=False)

    with caplog.at_level("INFO"):
        text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=None, config=cfg)

    assert text == "Launch plan ready."
    assert tools == []
    assert any("cognitive_loop_completion_event" in rec.message for rec in caplog.records)
    metric_recs = [rec for rec in caplog.records if "cognitive_loop_completion_event" in rec.message]
    assert metric_recs
    assert any("iterations=1" in rec.message or getattr(rec, "iterations_used", None) == 1 for rec in metric_recs)
