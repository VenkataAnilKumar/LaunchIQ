"""Deterministic offline stand-in for the Anthropic async client.

Selected with ``LLM_PROVIDER=fake``. It inspects the prompt to decide which
agent is calling and returns schema-valid canned JSON, including a tool_use
round-trip for agents that declare tools, so the whole pipeline (tool loop,
validation, HITL, persistence, streaming) can run without API keys.
"""
from __future__ import annotations

import json
import re
from types import SimpleNamespace
from typing import Any


def _block(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _response(content: list[SimpleNamespace], stop_reason: str, in_tok: int, out_tok: int):
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=in_tok, output_tokens=out_tok),
    )


def _last_user_text(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content
    return ""


def _has_tool_result(messages: list[dict[str, Any]]) -> bool:
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    return True
    return False


def _product(text: str) -> str:
    match = re.search(r"product_name:\s*(.+)", text)
    name = match.group(1).strip() if match else ""
    return name or "the product"


def _tool_result_urls(messages: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    urls += re.findall(r"https?://[^\s\"'\\]+", str(part.get("content", "")))
    return urls


def _market(name: str, urls: list[str] | None = None) -> dict[str, Any]:
    urls = urls or []
    src = lambda i: urls[i] if i < len(urls) else None
    return {
        "market_size": "$4.2B globally (fake data)",
        "growth_rate": "18% CAGR (fake data)",
        "competitors": [
            {
                "name": "Acme Launch",
                "positioning": "All-in-one launch suite for enterprises",
                "strengths": ["Brand recognition", "Integrations"],
                "weaknesses": ["Slow onboarding", "High price"],
                "pricing": "$499/mo",
            },
            {
                "name": "LaunchLite",
                "positioning": "Lightweight templates for solo founders",
                "strengths": ["Cheap", "Simple"],
                "weaknesses": ["No research depth"],
                "pricing": "$29/mo",
            },
        ],
        "trends": [
            {"trend": "AI-assisted go-to-market planning", "relevance": "High", "source": src(0)},
            {"trend": "Buyers expect self-serve onboarding", "relevance": "Medium", "source": src(1)},
        ],
        "white_space": "Fast, research-backed launch plans for small teams",
        "recommended_positioning": f"Position {name} as the fastest path from idea to launch-ready",
    }


def _persona(role: str, name: str) -> dict[str, Any]:
    return {
        "name": name,
        "role": role,
        "age_range": "28-45",
        "pain_points": ["Launch prep takes too long", "Unclear target segment"],
        "goals": ["Ship on time", "Hit pipeline targets"],
        "channels": ["LinkedIn", "Email", "Communities"],
        "message_hook": "Launch-ready in minutes, not months",
        "willingness_to_pay": "$50-200/mo",
    }


def _audience() -> dict[str, Any]:
    return {
        "primary_persona": _persona("Head of Product", "Priya the PM"),
        "secondary_personas": [_persona("Founder", "Sam the Founder")],
        "icp_summary": "Small product teams launching B2B software with no dedicated GTM staff",
        "messaging_framework": {
            "headline": "Launch with confidence",
            "proof": "Research-backed plan in minutes",
            "cta": "Create your launch brief",
        },
        "recommended_channels": ["LinkedIn", "Email", "Product Hunt"],
    }


def _strategy(name: str) -> dict[str, Any]:
    def phase(label: str, duration: str) -> dict[str, Any]:
        return {
            "phase": label,
            "duration": duration,
            "goals": ["Build awareness", "Convert early adopters"],
            "tactics": ["Teaser campaign", "Founder-led posts", "Partner outreach"],
            "kpis": ["Signups", "CTR"],
        }

    return {
        "positioning_statement": f"{name} gets small teams launch-ready faster than agencies.",
        "launch_date_recommendation": "Tuesday, three weeks out",
        "phases": [
            phase("Pre-Launch", "4 weeks"),
            phase("Launch Week", "1 week"),
            phase("Post-Launch", "4 weeks"),
            phase("Growth", "4 weeks"),
        ],
        "channels": ["LinkedIn", "Email", "Communities"],
        "budget_allocation": {"paid": "30%", "content": "40%", "events": "15%", "experiments": "15%"},
        "success_metrics": ["Qualified signups", "Activation rate"],
        "risks": ["Message dilution", "Slow follow-up"],
    }


def _items(kind: str, name: str) -> dict[str, Any]:
    def item(fmt: str, variant: str, n: int) -> dict[str, Any]:
        return {
            "format": fmt,
            "variant": variant,
            "headline": f"{name}: {kind} headline {n}{variant}",
            "body": f"Body copy for {kind} #{n}, variant {variant}.",
            "cta": "Get started",
            "target_persona": "Priya the PM",
        }

    if kind == "email":
        return {"items": [item("email", "a" if i % 2 == 0 else "b", i + 1) for i in range(3)]}
    if kind == "social":
        fmts = ["linkedin", "twitter", "linkedin"]
        return {"items": [item(f, "a" if i % 2 == 0 else "b", i + 1) for i, f in enumerate(fmts)]}
    return {"items": [item("ad_copy", "a", 1), item("ad_copy", "b", 2)]}


def _analytics() -> dict[str, Any]:
    return {
        "engagement_score": 0.52,
        "top_performing_content": ["LinkedIn thought-leadership post"],
        "underperforming_content": ["Low-CTR ad variant"],
        "recommendations": [
            {"area": "Ads", "insight": "Variant B CTR is low", "action": "Rewrite headline", "priority": "high"},
            {"area": "Email", "insight": "Open rate is healthy", "action": "Add a follow-up", "priority": "medium"},
            {"area": "Onboarding", "insight": "Activation lags signups", "action": "Shorten setup", "priority": "high"},
        ],
        "predicted_next_action": "Optimize onboarding and retest ad copy",
    }


def _fenced(payload: dict[str, Any]) -> str:
    return "```json\n" + json.dumps(payload) + "\n```"


class _FakeMessages:
    async def create(self, **params: Any) -> SimpleNamespace:
        messages = params.get("messages") or []
        prompt = _last_user_text(messages)
        tools = params.get("tools") or []

        if prompt.startswith("Review the following draft"):
            draft = prompt.split("DRAFT:\n", 1)[-1]
            return _response([_block(type="text", text=draft)], "end_turn", 50, 50)

        tokens_in = max(len(prompt) // 4, 1)

        # Tool round-trip: first call asks for a tool, second call returns the answer.
        if tools and not _has_tool_result(messages):
            tool = tools[0]
            name = tool["name"]
            tool_input = (
                {"query": f"{_product(prompt)} market competitors", "max_results": 3}
                if name == "tavily_search"
                else {"property_id": "properties/fake", "metrics": ["sessions"]}
            )
            return _response(
                [_block(type="tool_use", id="toolu_fake_1", name=name, input=tool_input)],
                "tool_use",
                tokens_in,
                20,
            )

        name = _product(prompt)
        thinking = []
        if params.get("thinking"):
            thinking = [_block(type="thinking", thinking="(fake) weighing channel trade-offs")]

        if "Generate market intelligence JSON" in prompt:
            payload = _market(name, _tool_result_urls(messages))
        elif "Generate audience insights" in prompt:
            payload = _audience()
        elif "Create launch strategy JSON" in prompt:
            payload = _strategy(name)
        elif "email items" in prompt:
            payload = _items("email", name)
        elif "social posts" in prompt:
            payload = _items("social", name)
        elif "ad copy items" in prompt:
            payload = _items("ad", name)
        elif "Analyze launch performance" in prompt:
            payload = _analytics()
        else:
            payload = {"note": "fake llm: unrecognised prompt"}

        text = _fenced(payload)
        return _response(
            [*thinking, _block(type="text", text=text)], "end_turn", tokens_in, max(len(text) // 4, 1)
        )


class FakeAnthropic:
    """Minimal async stand-in for ``anthropic.AsyncAnthropic``."""

    def __init__(self) -> None:
        self.messages = _FakeMessages()
