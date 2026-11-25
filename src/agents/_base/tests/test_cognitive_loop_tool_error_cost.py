"""Unit test for estimated cost inclusion in CognitiveLoop tool error metric."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_tool_error_metric_includes_estimated_cost(caplog):
    """When tokens have been used, tool error metric includes estimated_cost_usd."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
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

    with patch("src.agents._base.cognitive_loop.estimate_cost_usd", return_value=0.0123):
        with caplog.at_level("WARNING"):
            await run_tool_loop(mock_client, params, tool_executor=mock_executor, config=cfg)

    assert any("cognitive_loop_tool_error_event" in rec.message and "estimated_cost_usd" in rec.message for rec in caplog.records)
