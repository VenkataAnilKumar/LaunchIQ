"""Unit tests for the hard max_tool_calls limit in CognitiveLoop."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_max_tool_calls_stops_early(caplog):
    """Loop stops cleanly when max_tool_calls is reached, returning best text so far."""
    mock_client = MagicMock()

    tool_block = MagicMock(type="tool_use", name="search", input={"q": "test"}, id="t1")
    resp = MagicMock(stop_reason="tool_use", content=[tool_block])
    # Always return tool_use so we hit the cap
    mock_client.messages.create.return_value = resp

    mock_exec = MagicMock()
    mock_exec.execute = AsyncMock(return_value={"ok": True})

    params = {"messages": [{"role": "user", "content": "go"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(max_iterations=10, max_tool_calls=2, enable_reflection=False)

    with caplog.at_level("WARNING"):
        text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=mock_exec, config=cfg)

    assert len(tools) <= 2
    assert "max_tool_calls" in caplog.text.lower() or "tool calls" in caplog.text.lower()
    # Should not have crashed and should have returned some text or the stop marker
    assert isinstance(text, str)
