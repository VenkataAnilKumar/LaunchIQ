"""
Context builder — injects retrieved memory and RAG results into user messages.

Follows the Anthropic pattern of constructing a rich context block before
the user's actual request so the model reasons from grounded information.
"""
from __future__ import annotations

from typing import Any


_CONTEXT_TEMPLATE = """\
<context>
{sections}
</context>

{user_message}"""

_SECTION_TEMPLATE = "<{tag}>\n{content}\n</{tag}>"


class ContextBuilder:
    """Assembles structured context blocks around a user message."""

    def inject(self, user_message: str, context: dict[str, Any]) -> str:
        sections: list[str] = []

        if market_data := context.get("market_data"):
            sections.append(_SECTION_TEMPLATE.format(tag="market_data", content=_fmt(market_data)))

        if personas := context.get("personas"):
            sections.append(_SECTION_TEMPLATE.format(tag="personas", content=_fmt(personas)))

        if brand_voice := context.get("brand_voice"):
            sections.append(_SECTION_TEMPLATE.format(tag="brand_voice", content=_fmt(brand_voice)))

        if session_memory := context.get("session_memory"):
            sections.append(
                _SECTION_TEMPLATE.format(tag="session_memory", content=_fmt(session_memory))
            )

        if prior_outputs := context.get("prior_outputs"):
            sections.append(
                _SECTION_TEMPLATE.format(tag="prior_agent_outputs", content=_fmt(prior_outputs))
            )

        if not sections:
            return user_message

        return _CONTEXT_TEMPLATE.format(
            sections="\n\n".join(sections),
            user_message=user_message,
        )


def _fmt(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)
