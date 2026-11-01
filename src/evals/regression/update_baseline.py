#!/usr/bin/env python3
"""Write the current metrics into baseline.json for the chosen mode.

Only run this deliberately (e.g. after a live run you have reviewed): the baseline is what
the PR gate enforces. ``--if-improved`` only tightens thresholds, never loosens them.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from src.evals.regression.run_regression import (
	BASELINE_PATH,
	TRACKED,
	run,
)


def main() -> None:
	parser = argparse.ArgumentParser(description="Update eval baseline")
	parser.add_argument("--offline", action="store_true")
	parser.add_argument("--if-improved", action="store_true", help="Only tighten thresholds")
	args = parser.parse_args()

	if args.offline:
		os.environ["LLM_PROVIDER"] = "fake"
		os.environ["SEARCH_PROVIDER"] = "fake"
	elif not os.getenv("ANTHROPIC_API_KEY"):
		print("BASELINE PRECHECK FAILED: set ANTHROPIC_API_KEY, or use --offline.", file=sys.stderr)
		raise SystemExit(2)

	from src.evals.framework.evaluator import LOWER_IS_BETTER

	mode = "offline" if args.offline else "live"
	results = asyncio.run(run(None))
	data = json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.exists() else {}
	section = data.setdefault(mode, {})
	section.pop("_note", None)
	for agent_id, summary in results.items():
		current = section.setdefault(agent_id, {})
		for metric in TRACKED:
			if metric not in summary:
				continue
			new = round(float(summary[metric]), 4)
			old = current.get(metric)
			better = old is None or (new < old if metric in LOWER_IS_BETTER else new > old)
			if not args.if_improved or better:
				current[metric] = new
	BASELINE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
	print(f"Baseline ({mode}) updated at {BASELINE_PATH}")


if __name__ == "__main__":
	main()
