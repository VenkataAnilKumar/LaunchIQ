"""Unit tests for CognitiveLoop (mocked Anthropic client)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop, _truncate_tool_result


@pytest.mark.asyncio
async def test_run_tool_loop_end_turn_no_tools():
    """Simple end_turn path returns text without tools."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(type="text", text="Final launch strategy.")]
    mock_client.messages.create.return_value = mock_response

    params = {"messages": [{"role": "user", "content": "Analyze market"}], "model": "claude-sonnet-4-6"}
    text, tools, thinking = await run_tool_loop(mock_client, params, tool_executor=None, config=LoopConfig(enable_reflection=False))

    assert text == "Final launch strategy."
    assert tools == []
    assert thinking is None
    mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_run_tool_loop_handles_tool_error():
    """Tool execution exceptions are captured in tool_log and do not crash the loop."""
    mock_client = MagicMock()

    # First response: tool_use
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "search_market"
    tool_block.input = {"query": "competitors"}
    tool_block.id = "toolu_01"

    resp1 = MagicMock()
    resp1.stop_reason = "tool_use"
    resp1.content = [tool_block]

    # Second response: end_turn
    resp2 = MagicMock()
    resp2.stop_reason = "end_turn"
    resp2.content = [MagicMock(type="text", text="Strategy complete.")]

    mock_client.messages.create.side_effect = [resp1, resp2]

    async def failing_executor(name, inp):
        raise RuntimeError("API rate limit")

    mock_executor = MagicMock()
    mock_executor.execute = failing_executor

    params = {"messages": [], "model": "claude-sonnet-4-6"}
    text, tools, _ = await run_tool_loop(
        mock_client, params, tool_executor=mock_executor, config=LoopConfig(enable_reflection=False, max_iterations=5)
    )

    assert text == "Strategy complete."
    assert len(tools) == 1
    assert tools[0]["tool_name"] == "search_market"
    assert "error" in tools[0]["output"]
    assert "rate limit" in tools[0]["output"]["error"]


@pytest.mark.asyncio
async def test_reflection_is_skipped_when_disabled():
    """Reflection path is not invoked when enable_reflection=False."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(type="text", text="Draft content.")]
    mock_client.messages.create.return_value = mock_response

    with patch("src.agents._base.cognitive_loop._maybe_reflect", new_callable=AsyncMock) as mock_reflect:
        params = {"messages": [{"role": "user", "content": "hi"}]}
        await run_tool_loop(mock_client, params, None, config=LoopConfig(enable_reflection=False))
        mock_reflect.assert_not_called()


@pytest.mark.asyncio
async def test_max_iterations_warning_path():
    """Hitting max_iterations returns last text and logs warning (no crash)."""
    mock_client = MagicMock()
    # Always return tool_use so we hit the limit
    tool_block = MagicMock(type="tool_use", name="dummy", input={}, id="t1")
    resp = MagicMock(stop_reason="tool_use", content=[tool_block])
    mock_client.messages.create.return_value = resp

    mock_executor = MagicMock()
    mock_executor.execute = AsyncMock(return_value={"ok": True})

    params = {"messages": []}
    text, tools, _ = await run_tool_loop(
        mock_client, params, tool_executor=mock_executor, config=LoopConfig(max_iterations=2, enable_reflection=False)
    )

    # Should have executed tools up to the limit and returned whatever text was last (empty here)
    assert isinstance(tools, list)
    assert mock_client.messages.create.call_count == 2


def test_truncate_tool_result_small():
    """Small results pass through unchanged."""
    small = {"data": "ok"}
    assert _truncate_tool_result(small) == small


def test_truncate_tool_result_large():
    """Large results are truncated with a marker."""
    large = {"data": "x" * 3000}
    out = _truncate_tool_result(large)
    assert isinstance(out, dict)
    assert out.get("truncated") is True
    assert "original_length" in out
    assert len(json.dumps(out)) < 3000  # type: ignore
