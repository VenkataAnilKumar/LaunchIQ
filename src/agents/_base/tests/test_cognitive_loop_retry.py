"""Unit test for CognitiveLoop LLM retry metric events."""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock

import pytest

from src.agents._base.cognitive_loop import LoopConfig, run_tool_loop


@pytest.mark.asyncio
async def test_retry_metric_emitted_on_transient_failure(caplog):
    """When the LLM call fails then succeeds on retry, emit cognitive_loop_retry_event."""
    mock_client = MagicMock()
    success_response = MagicMock()
    success_response.stop_reason = "end_turn"
    success_response.content = [MagicMock(type="text", text="Recovered.")]

    # First call raises, second succeeds
    mock_client.messages.create = AsyncMock(side_effect=[Exception("rate limit"), success_response])

    params = {"messages": [{"role": "user", "content": "Test"}], "model": "claude-sonnet-4-6"}
    cfg = LoopConfig(max_api_retries=1, retry_backoff_seconds=0.01)

    with caplog.at_level("INFO"):
        text, tools, _ = await run_tool_loop(mock_client, params, tool_executor=None, config=cfg)

    assert text == "Recovered."
    assert any("cognitive_loop_retry_event" in rec.message for rec in caplog.records)
    assert any("attempt=1" in rec.message or getattr(rec, "attempt", None) == 1 for rec in caplog.records)
