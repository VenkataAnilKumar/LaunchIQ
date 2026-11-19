"""Unit test for CognitiveLoop tool error metric events."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_tool_error_metric_emitted_on_execution_failure(caplog):
    """When tool executor raises, emit cognitive_loop_tool_error_event."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    tool_use = MagicMock()
    tool_use.type = "tool_use"
    tool_use.name = "market_search"
    tool_use.input = {"query": "competitors"}
    tool_use.id = "tu1"
    mock_response.content = [tool_use]
    mock_client.messages.create.return_value = mock_response

    async def failing_execute(name, inp):
        raise RuntimeError("network timeout")

    mock_executor = MagicMock()
    mock_executor.execute = failing_execute

    params = {"messages": [{"role": "user", "content": "Research"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(max_tool_calls=5, max_iterations=2)

    with caplog.at_level("WARNING"):
        text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=mock_executor, config=cfg)

    assert any("cognitive_loop_tool_error_event" in rec.message for rec in caplog.records)
    assert any("market_search" in rec.message for rec in caplog.records)
