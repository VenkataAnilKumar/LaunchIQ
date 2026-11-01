#!/usr/bin/env python3
"""Run the eval corpus through the real agents and gate on the baseline.

  --offline   fake LLM + fake search (no keys). Verifies plumbing and safety behaviour on
              every corpus brief, deterministically. Does NOT measure model quality.
  (default)   live Anthropic/Tavily calls. Needs ANTHROPIC_API_KEY. Measures real quality
              and cost; use for the scheduled run and before changing prompts/models.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"
TRACKED = (
	"schema_compliance",
	"hallucination_rate",
	"error_rate",
	"citation_coverage",
	"product_mention",
	"injection_leak_rate",
)


def load_baseline(mode: str) -> dict[str, dict[str, float]]:
	if not BASELINE_PATH.exists():
		return {}
	data = json.loads(BASELINE_PATH.read_text(encoding="utf-8") or "{}")
	section = data.get(mode, {})
	return {k: v for k, v in section.items() if isinstance(v, dict)}


def check_baseline(results: dict[str, dict[str, Any]], baseline: dict[str, dict[str, float]]) -> list[str]:
	from src.evals.framework.evaluator import LOWER_IS_BETTER

	failures: list[str] = []
	for agent_id, expected in baseline.items():
		actual = results.get(agent_id)
		if actual is None:
			failures.append(f"{agent_id}: missing from results")
			continue
		for metric, threshold in expected.items():
			if metric not in actual:
				failures.append(f"{agent_id}.{metric}: not produced")
				continue
			value = float(actual[metric])
			if metric in LOWER_IS_BETTER:
				if value > threshold:
					failures.append(f"{agent_id}.{metric}: {value:.4f} > {threshold:.4f}")
			elif value < threshold:
				failures.append(f"{agent_id}.{metric}: {value:.4f} < {threshold:.4f}")
	return failures


def print_summary(results: dict[str, dict[str, Any]]) -> None:
	cols = ("total_cases", *TRACKED, "tokens", "cost_usd")
	print("agent".ljust(22) + " ".join(c[:14].rjust(14) for c in cols))
	for agent_id, r in results.items():
		print(agent_id.ljust(22) + " ".join(str(r.get(c, "-"))[:14].rjust(14) for c in cols))
	for agent_id, r in results.items():
		for err in r.get("errors", []):
			print(f"  ERROR {agent_id} [{err['brief']}]: {err['error'][:160]}")


async def run(agent: str | None) -> dict[str, dict[str, Any]]:
	from src.agents._base.llm import reset_client
	from src.apps.api.config import get_settings
	from src.evals.framework.evaluator import PIPELINE, Evaluator

	get_settings.cache_clear()
	reset_client()
	return await Evaluator().run_corpus(agents=[agent] if agent else PIPELINE)


def main() -> None:
	parser = argparse.ArgumentParser(description="Run LaunchIQ eval regression")
	parser.add_argument("--assert-baseline", action="store_true", help="Fail when metrics regress")
	parser.add_argument("--agent", help="Run only one agent (earlier agents still run to feed it)")
	parser.add_argument("--offline", action="store_true", help="Fake LLM/search; no API keys required")
	parser.add_argument("--json", action="store_true", help="Print full JSON results")
	args = parser.parse_args()

	if args.offline:
		os.environ["LLM_PROVIDER"] = "fake"
		os.environ["SEARCH_PROVIDER"] = "fake"
	elif not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
		print("EVAL PRECHECK FAILED: set ANTHROPIC_API_KEY, or use --offline.", file=sys.stderr)
		sys.exit(2)

	mode = "offline" if args.offline else "live"
	results = asyncio.run(run(args.agent))
	print(f"mode: {mode}")
	print_summary(results)
	if args.json:
		print(json.dumps(results, indent=2))

	if args.assert_baseline:
		failures = check_baseline(results, load_baseline(mode))
		if failures:
			print("\nEVAL GATE FAILED", file=sys.stderr)
			for failure in failures:
				print(f"- {failure}", file=sys.stderr)
			sys.exit(1)
		print("\nEval gate passed.")


if __name__ == "__main__":
	main()
