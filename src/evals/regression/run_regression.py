#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any


AGENTS = [
	"market_intelligence",
	"audience_insight",
	"launch_strategy",
	"content_generation",
]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

REGRESSION_DIR = Path(__file__).resolve().parent
BASELINE_PATH = REGRESSION_DIR / "baseline.json"
SUITES_ROOT = REGRESSION_DIR.parent / "suites"


def _load_json(path: Path, fallback: Any) -> Any:
	if not path.exists():
		return fallback
	content = path.read_text(encoding="utf-8").strip()
	if not content:
		return fallback
	return json.loads(content)


def _load_baseline() -> dict[str, dict[str, float]]:
	baseline = _load_json(BASELINE_PATH, {})
	if not isinstance(baseline, dict):
		return {}
	return baseline


def _ensure_eval_credentials() -> None:
	# Anthropic SDK supports API key or auth token. Require one up front for eval runs.
	has_api_key = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
	has_auth_token = bool(os.getenv("ANTHROPIC_AUTH_TOKEN", "").strip())
	if has_api_key or has_auth_token:
		return

	raise RuntimeError(
		"Missing Anthropic credentials for evals. Set ANTHROPIC_API_KEY "
		"(recommended) or ANTHROPIC_AUTH_TOKEN before running regression suites."
	)


def _print_summary(results: dict[str, dict[str, Any]], baseline: dict[str, dict[str, float]]) -> None:
	print("agent | relevance | baseline | hallucination | baseline | schema | baseline")
	print("-" * 76)
	for agent_id, summary in results.items():
		agent_baseline = baseline.get(agent_id, {})
		print(
			f"{agent_id} | "
			f"{summary.get('relevance_score', 0.0):.4f} | {agent_baseline.get('relevance_score', 0.0):.4f} | "
			f"{summary.get('hallucination_rate', 1.0):.4f} | {agent_baseline.get('hallucination_rate', 1.0):.4f} | "
			f"{summary.get('schema_compliance', 0.0):.4f} | {agent_baseline.get('schema_compliance', 0.0):.4f}"
		)


def check_baseline(results: dict[str, dict[str, Any]], baseline: dict[str, dict[str, float]]) -> list[str]:
	failures: list[str] = []
	for agent_id, actual_metrics in results.items():
		expected_metrics = baseline.get(agent_id, {})
		if not expected_metrics:
			continue
		for metric, threshold in expected_metrics.items():
			actual_value = float(actual_metrics.get(metric, 0.0))
			if metric == "hallucination_rate":
				if actual_value > threshold:
					failures.append(f"{agent_id}.{metric}: {actual_value:.4f} > {threshold:.4f}")
			else:
				if actual_value < threshold:
					failures.append(f"{agent_id}.{metric}: {actual_value:.4f} < {threshold:.4f}")
	return failures


async def run_all_suites(agent: str | None = None, *, offline: bool = False) -> dict[str, dict[str, Any]]:
	from src.evals.framework.evaluator import Evaluator

	evaluator = Evaluator(offline=offline)
	agent_ids = [agent] if agent else AGENTS
	results: dict[str, dict[str, Any]] = {}

	for agent_id in agent_ids:
		suite_dir = SUITES_ROOT / agent_id
		test_cases = _load_json(suite_dir / "test_cases.json", [])
		expected = _load_json(suite_dir / "expected_outputs.json", [])
		results[agent_id] = await evaluator.run_suite(agent_id, test_cases, expected)

	return results


def main() -> None:
	parser = argparse.ArgumentParser(description="Run LaunchIQ eval regression suites")
	parser.add_argument("--assert-baseline", action="store_true", help="Fail when metrics regress")
	parser.add_argument("--agent", choices=AGENTS, help="Run only one agent suite")
	parser.add_argument("--offline", action="store_true", help="Use deterministic mock outputs (no API keys required)")
	args = parser.parse_args()

	if not args.offline:
		try:
			_ensure_eval_credentials()
		except RuntimeError as exc:
			print(f"EVAL PRECHECK FAILED: {exc}", file=sys.stderr)
			sys.exit(2)

	results = asyncio.run(run_all_suites(args.agent, offline=args.offline))
	baseline = _load_baseline()

	_print_summary(results, baseline)
	print(json.dumps(results, indent=2))

	if args.assert_baseline:
		failures = check_baseline(results, baseline)
		if failures:
			print("\nEVAL GATE FAILED", file=sys.stderr)
			for failure in failures:
				print(f"- {failure}", file=sys.stderr)
			sys.exit(1)
		print("\nEval gate passed.")


if __name__ == "__main__":
	main()
