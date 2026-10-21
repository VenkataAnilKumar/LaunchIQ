"""
Context builder — injects retrieved memory and RAG results into user messages.

Follows the Anthropic pattern of constructing a rich context block before
the user's actual request so the model reasons from grounded information.

Enhancements:
- Per-section truncation to keep prompts within practical token budgets
- Additional supported sections (tool_history, constraints)
- More robust formatting for nested data
"""
from __future__ import annotations

from typing import Any

_CONTEXT_TEMPLATE = """\
<context>
{sections}
</context>

{user_message}"""

_SECTION_TEMPLATE = "<{tag}>\n{content}\n</{tag}>"

# Soft limit per section (characters). Prevents a single large RAG blob from dominating the prompt.
_MAX_SECTION_CHARS = 4000


class ContextBuilder:
    """Assembles structured context blocks around a user message."""

    def inject(
        self,
        user_message: str,
        context: dict[str, Any],
        max_section_chars: int = _MAX_SECTION_CHARS,
    ) -> str:
        sections: list[str] = []

        # Ordered for typical pipeline flow (market → audience → brand → memory → tools → constraints)
        section_map = [
            ("market_data", "market_data"),
            ("personas", "personas"),
            ("brand_voice", "brand_voice"),
            ("session_memory", "session_memory"),
            ("prior_outputs", "prior_agent_outputs"),
            ("tool_history", "tool_history"),
            ("constraints", "constraints"),
        ]

        for key, tag in section_map:
            if value := context.get(key):
                content = _fmt(value)
                content = _truncate(content, max_section_chars)
                sections.append(_SECTION_TEMPLATE.format(tag=tag, content=content))

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
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{k}:")
                lines.append(_fmt(v))
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)
    if isinstance(value, list):
        return "\n".join(f"- {_fmt(item) if not isinstance(item, str) else item}" for item in value)
    return str(value)


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20] + "\n... [truncated]"
