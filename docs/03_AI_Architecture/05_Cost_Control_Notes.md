# Cost Control and Reliability Notes for CognitiveLoop

## Status

Recent enhancement (2026-11-05): CognitiveLoop now estimates running cost after each API call and stops early if `cost_budget_usd` is exceeded, returning the best text so far. Structured logs capture the early stop.

## Rationale

Prevents runaway spend on long tool chains or repeated reflections while preserving partial useful output. Complements the existing post-run budget status.

## Suggested Next Steps

1. Add a hard `max_tool_calls` (e.g. 8) independent of cost, with clear logging.
2. Include reflection-pass tokens more precisely in running estimates.
3. Emit Prometheus-style metrics or structured events for budget approach / breach so dashboards can alert.
4. Optional: soft warning at 80% of budget that can be used by HITL UI.

## References

- `src/agents/_base/cognitive_loop.py`
- Recent tests in `src/agents/_base/tests/test_cognitive_loop_budget.py`
