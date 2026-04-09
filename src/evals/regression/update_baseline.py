#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from src.evals.regression.run_regression import run_all_suites
from src.evals.regression.run_regression import _ensure_eval_credentials


BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"
TRACKED_METRICS = ("relevance_score", "hallucination_rate", "schema_compliance")


def _read_json(path: Path) -> dict[str, Any]:
	if not path.exists():
		return {}
	content = path.read_text(encoding="utf-8").strip()
	if not content:
		return {}
	loaded = json.loads(content)
	return loaded if isinstance(loaded, dict) else {}


def _is_improved(metric: str, new_val: float, old_val: float) -> bool:
	if metric == "hallucination_rate":
		return new_val < old_val
	return new_val > old_val


def _merge_if_improved(
	current: dict[str, dict[str, float]],
	candidate: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
	merged: dict[str, dict[str, float]] = {agent: values.copy() for agent, values in current.items()}

	for agent_id, metrics in candidate.items():
		agent_metrics = merged.setdefault(agent_id, {})
		for metric in TRACKED_METRICS:
			new_val = float(metrics.get(metric, 0.0))
			old_val = float(agent_metrics.get(metric, 0.0))
			if metric not in agent_metrics or _is_improved(metric, new_val, old_val):
				agent_metrics[metric] = round(new_val, 4)

	return merged


def main() -> None:
	parser = argparse.ArgumentParser(description="Update eval regression baseline")
	parser.add_argument(
		"--if-improved",
		action="store_true",
		help="Only update baseline metrics that improved",
	)
	parser.add_argument(
		"--offline",
		action="store_true",
		help="Use deterministic mock outputs (no API keys required)",
	)
	args = parser.parse_args()

	if not args.offline:
		try:
			_ensure_eval_credentials()
		except RuntimeError as exc:
			print(f"BASELINE PRECHECK FAILED: {exc}")
			raise SystemExit(2) from exc

	results = asyncio.run(run_all_suites(offline=args.offline))
	candidate: dict[str, dict[str, float]] = {}
	for agent_id, summary in results.items():
		candidate[agent_id] = {
			metric: round(float(summary.get(metric, 0.0)), 4)
			for metric in TRACKED_METRICS
		}

	if args.if_improved:
		current = _read_json(BASELINE_PATH)
		output = _merge_if_improved(current, candidate)
	else:
		output = candidate

	BASELINE_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
	print(f"Baseline updated at {BASELINE_PATH}")


if __name__ == "__main__":
	main()
