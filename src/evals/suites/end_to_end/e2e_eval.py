"""End-to-end pipeline evaluation suite.

Tests the full launch pipeline: orchestrator + all 4 agents.
Validates that all agents run correctly and produce schema-valid output.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

SUITE_DIR = Path(__file__).parent


async def run_e2e() -> dict:
    """Run full pipeline E2E: orchestrator → 4 agents → validate outputs."""
    from src.agents.orchestrator.agent import OrchestratorAgent
    from src.agents.orchestrator.schemas import OrchestratorOutput

    test_cases = json.loads((SUITE_DIR / "test_cases.json").read_text())
    if not test_cases:
        return {
            "suite": "end_to_end",
            "passed": False,
            "error": "No test cases found in test_cases.json",
        }

    brief = test_cases[0]["input"]

    agent = OrchestratorAgent()
    result = await agent.run(brief)

    try:
        output = OrchestratorOutput(**result.output)
    except Exception as e:
        return {
            "suite": "end_to_end",
            "passed": False,
            "error": f"OrchestratorOutput validation failed: {e}",
        }

    checks = {
        "all_agents_ran": len(output.agent_outputs) >= 4,
        "no_agent_failed": output.status == "completed",
        "market_intelligence_present": "market_intelligence" in output.agent_outputs,
        "audience_insight_present": "audience_insight" in output.agent_outputs,
        "launch_strategy_present": "launch_strategy" in output.agent_outputs,
        "content_generation_present": "content_generation" in output.agent_outputs,
        "pipeline_status_completed": output.status == "completed",
    }

    return {
        "suite": "end_to_end",
        "passed": all(v is True for v in checks.values() if isinstance(v, bool)),
        "checks": checks,
        "agent_outputs_count": len(output.agent_outputs),
        "pipeline_status": output.status,
    }


if __name__ == "__main__":
    result = asyncio.run(run_e2e())
    print(json.dumps(result, indent=2))
