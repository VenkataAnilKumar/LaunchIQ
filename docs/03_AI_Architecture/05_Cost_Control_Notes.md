# Cost Control and Reliability Notes for CognitiveLoop

## Status

- 2026-11-05: Mid-loop cost budget enforcement (stops early, returns best text so far).
- 2026-11-07: Hard `max_tool_calls` (default 8) independent of cost, with clear warning log. Mid-loop budget check now runs after every API response.
- 2026-11-08: Soft INFO warning when estimated cost exceeds 80% of budget (budget_status=approaching). Structured extra payload for easy dashboarding.

## Rationale

Prevents runaway spend on long tool chains or repeated reflections while preserving partial useful output. The tool-call cap provides a second independent safety net even when token pricing estimates are imperfect. The 80% approaching signal enables proactive HITL or alerting before a hard stop.

## Suggested Next Steps

1. Include reflection-pass tokens more precisely in running estimates.
2. Emit Prometheus-style metrics or structured events for budget approach / breach so dashboards can alert.
3. Per-agent configurable tool-call budgets (strategy agent may need more than market).
4. Optional: surface approaching status to the review UI for human awareness.

## References

- `src/agents/_base/cognitive_loop.py`
- `src/agents/_base/tests/test_cognitive_loop_budget.py`
- `src/agents/_base/tests/test_cognitive_loop_max_tools.py`
