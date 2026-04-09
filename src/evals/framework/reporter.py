from __future__ import annotations

from typing import Any


class Reporter:
	def summarize(self, agent_id: str, results: list[dict[str, Any]]) -> dict[str, Any]:
		if not results:
			return {
				"agent_id": agent_id,
				"total_cases": 0,
				"relevance_score": 0.0,
				"hallucination_rate": 1.0,
				"schema_compliance": 0.0,
				"pass_fail": {
					"relevance_score": False,
					"hallucination_rate": False,
					"schema_compliance": False,
				},
			}

		metrics = ("relevance_score", "hallucination_rate", "schema_compliance")
		averages: dict[str, float] = {}
		for metric in metrics:
			values = [float(item.get("scores", {}).get(metric, 0.0)) for item in results]
			averages[metric] = round(sum(values) / len(values), 4)

		pass_fail = {
			"relevance_score": averages["relevance_score"] >= 0.75,
			"hallucination_rate": averages["hallucination_rate"] <= 0.05,
			"schema_compliance": averages["schema_compliance"] >= 0.95,
		}

		return {
			"agent_id": agent_id,
			"total_cases": len(results),
			**averages,
			"pass_fail": pass_fail,
		}

	def print_report(self, summary: dict[str, Any]) -> None:
		headers = ("agent", "cases", "relevance", "hallucination", "schema")
		row = (
			summary.get("agent_id", "unknown"),
			str(summary.get("total_cases", 0)),
			f"{summary.get('relevance_score', 0.0):.4f}",
			f"{summary.get('hallucination_rate', 1.0):.4f}",
			f"{summary.get('schema_compliance', 0.0):.4f}",
		)

		line = " | ".join(headers)
		print(line)
		print("-" * len(line))
		print(" | ".join(row))
