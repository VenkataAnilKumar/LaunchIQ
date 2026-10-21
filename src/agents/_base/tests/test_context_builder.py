"""Unit tests for ContextBuilder."""
from __future__ import annotations

from src.agents._base.context_builder import ContextBuilder


def test_inject_empty_context_returns_original():
    builder = ContextBuilder()
    msg = "Create a launch plan for Acme."
    assert builder.inject(msg, {}) == msg


def test_inject_includes_supported_sections():
    builder = ContextBuilder()
    context = {
        "market_data": {"competitors": ["A", "B"], "trend": "rising"},
        "personas": [{"name": "Founder", "pain": "time"}],
        "brand_voice": "Direct and data-driven",
        "session_memory": "User prefers concise outputs",
        "tool_history": [{"tool": "search", "result": "ok"}],
        "constraints": "Stay under $10k budget",
    }
    result = builder.inject("Generate content", context)
    assert "<context>" in result
    assert "<market_data>" in result
    assert "<personas>" in result
    assert "<brand_voice>" in result
    assert "<session_memory>" in result
    assert "<tool_history>" in result
    assert "<constraints>" in result
    assert "Generate content" in result
    assert result.endswith("Generate content")


def test_inject_truncates_long_sections():
    builder = ContextBuilder()
    long_text = "x" * 5000
    context = {"market_data": long_text}
    result = builder.inject("Plan", context, max_section_chars=100)
    assert "[truncated]" in result
    assert len(result) < 5000  # rough sanity


def test_inject_handles_nested_structures():
    builder = ContextBuilder()
    context = {
        "prior_outputs": {
            "strategy": {"phases": ["prep", "launch", "scale"], "risk": "medium"}
        }
    }
    result = builder.inject("Next step", context)
    assert "<prior_agent_outputs>" in result
    assert "phases" in result
    assert "prep" in result
