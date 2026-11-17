# Cost Control and Reliability Notes for CognitiveLoop

## Status

- 2026-11-05: Mid-loop cost budget enforcement (stops early, returns best text so far).
- 2026-11-07: Hard `max_tool_calls` (default 8) independent of cost, with clear warning log. Mid-loop budget check now runs after every API response.
- 2026-11-08: Soft INFO warning when estimated cost exceeds 80% of budget (budget_status=approaching). Structured extra payload for easy dashboarding.
- 2026-11-09: Optional reflection pass implemented. Reflection tokens are accumulated into the running estimate and the budget is re-checked; if exceeded, the original text is kept. Structured logs note the phase.
- 2026-11-10: Structured budget metric events (`metric=cognitive_loop_budget_event`) emitted for approaching and exceeded states. Consistent payload enables dashboard alerts without a metrics library.
- 2026-11-11: Structured tool-call metric events (`metric=cognitive_loop_tool_event`) emitted when the hard max_tool_calls limit is reached. Consistent payload enables dashboard alerts without a metrics library.
- 2026-11-12: `max_tool_calls` now flows correctly through BaseAgent._call_with_tools and is configurable per agent via AgentConfig.max_tool_calls.
- 2026-11-13: Reflection pass is now configurable per agent via AgentConfig.enable_reflection (default remains False).
- 2026-11-14: Structured reflection metric events (`metric=cognitive_loop_reflection_event`) emitted with change status, character counts, and delta. Enables quality and cost monitoring of the optional pass.
- 2026-11-15: Structured truncation metric events (`metric=cognitive_loop_truncation_event`) emitted when tool results are truncated. Enables monitoring of context pressure from large tool outputs.
- 2026-11-16: Soft budget approaching threshold is now configurable via LoopConfig.budget_approaching_threshold (default 0.8). Structured iteration metric events (`metric=cognitive_loop_iteration_event`) emitted when max_iterations is reached.
- 2026-11-17: Structured completion metric events (`metric=cognitive_loop_completion_event`) emitted on normal loop exits with iterations used and tool calls made.

## Rationale

Prevents runaway spend on long tool chains or repeated reflections while preserving partial useful output. The tool-call cap provides a second independent safety net even when token pricing estimates are imperfect. The configurable approaching signal and explicit metric events (budget, tool, reflection, truncation, iteration, and completion) enable proactive HITL or alerting before a hard stop, and make successful outcomes measurable. Reflection is opt-in and budget-aware so quality improvements do not silently exceed limits. Per-agent tool budgets and reflection flags let higher-reasoning agents (strategy) use more tools or reflection without raising the global default. Reflection, truncation, iteration, and completion metrics make the quality, context, loop-exhaustion, and efficiency impact of the loop measurable.

## Suggested Next Steps

1. ~~Emit Prometheus-style metrics or structured events for budget approach / breach so dashboards can alert.~~ **Done 2026-11-10** (structured log events).
2. ~~Emit structured events for tool-call limit so dashboards can alert.~~ **Done 2026-11-11** (structured log events).
3. ~~Per-agent configurable tool-call budgets (strategy agent may need more than market).~~ **Done 2026-11-12** (AgentConfig.max_tool_calls).
4. ~~Make reflection configurable per agent (e.g., only strategy).~~ **Done 2026-11-13** (AgentConfig.enable_reflection).
5. ~~Structured reflection metric events for quality/cost tracking.~~ **Done 2026-11-14**.
6. ~~Structured truncation metric events for context pressure tracking.~~ **Done 2026-11-15**.
7. ~~Make soft budget threshold configurable and emit max-iterations metric.~~ **Done 2026-11-16**.
8. ~~Structured completion metric events for successful outcomes.~~ **Done 2026-11-17**.
9. Optional: surface approaching status to the review UI for human awareness.
10. Add a quality eval for the reflection improvement.

## References

- `src/agents/_base/cognitive_loop.py` (`_emit_budget_metric`, `_emit_tool_metric`, `_emit_reflection_metric`, `_emit_truncation_metric`, `_emit_iteration_metric`, `_emit_completion_metric`, `run_tool_loop`, `CognitiveLoop`, `LoopConfig`)
- `src/agents/_base/base_agent.py` (`AgentConfig`, `_call_with_tools`)
- `src/agents/_base/tests/test_cognitive_loop_budget.py`
- `src/agents/_base/tests/test_cognitive_loop_max_tools.py`
- `src/agents/_base/tests/test_cognitive_loop_reflection.py`
