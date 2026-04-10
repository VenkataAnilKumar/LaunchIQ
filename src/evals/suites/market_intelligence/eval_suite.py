"""Market Intelligence agent evaluation suite."""
from __future__ import annotations

import json
from pathlib import Path

from src.evals.framework.evaluator import Evaluator
from src.agents.market_intelligence.schemas import MarketIntelligenceOutput

SUITE_DIR = Path(__file__).parent


async def run_suite() -> dict:
    """Run Market Intelligence eval suite against test cases and expected outputs."""
    evaluator = Evaluator()
    test_cases = json.loads((SUITE_DIR / "test_cases.json").read_text())
    expected = json.loads((SUITE_DIR / "expected_outputs.json").read_text())
    return await evaluator.run_suite("market_intelligence", test_cases, expected)


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_suite())
    print(json.dumps(result, indent=2))
