"""Unit test for CognitiveLoop tool timeout metric events."""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_tool_timeout_metric_emitted_on_timeout(caplog):
    """When tool executor times out, emit cognitive_loop_tool_timeout_event."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    tool_use = MagicMock()
    tool_use.type = "tool_use"
    tool_use.name = "slow_search"
    tool_use.input = {"query": "competitors"}
    tool_use.id = "tu1"
    mock_response.content = [tool_use]
    mock_client.messages.create.return_value = mock_response

    async def slow_execute(name, inp):
        await asyncio.sleep(10)  # longer than the configured timeout
        return {"ok": True}

    mock_executor = MagicMock()
    mock_executor.execute = slow_execute

    params = {"messages": [{"role": "user", "content": "Research"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(max_tool_calls=5, max_iterations=2, tool_timeout_seconds=0.1)

    with caplog.at_level("WARNING"):
        text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=mock_executor, config=cfg)

    assert any("cognitive_loop_tool_timeout_event" in rec.message for rec in caplog.records)
    assert any("slow_search" in rec.message for rec in caplog.records)
    # Also still emits the general error metric
    assert any("cognitive_loop_tool_error_event" in rec.message for rec in caplog.records)
