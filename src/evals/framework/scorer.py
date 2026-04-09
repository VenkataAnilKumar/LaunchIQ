from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.evals.metrics.edit_rate import EditRateScorer
from src.evals.metrics.hallucination import HallucinationScorer
from src.evals.metrics.relevance import RelevanceScorer
from src.evals.metrics.schema_compliance import SchemaComplianceScorer


class Scorer:
	def __init__(self) -> None:
		self.relevance = RelevanceScorer()
		self.hallucination = HallucinationScorer()
		self.schema_compliance = SchemaComplianceScorer()
		self.edit_rate = EditRateScorer()

	def score(
		self,
		actual: dict[str, Any],
		expected: dict[str, Any],
		*,
		context: dict[str, Any] | None = None,
		schema_class: type[BaseModel] | None = None,
		original_output: dict[str, Any] | None = None,
		edited_output: dict[str, Any] | None = None,
	) -> dict[str, float]:
		relevance_score = self.relevance.score(actual, expected)
		hallucination_rate = self.hallucination.score(actual, context)
		schema_score = self.schema_compliance.score(actual, schema_class)

		scores: dict[str, float] = {
			"relevance_score": relevance_score,
			"hallucination_rate": hallucination_rate,
			"schema_compliance": schema_score,
		}

		if original_output is not None and edited_output is not None:
			scores["edit_rate"] = self.edit_rate.score(original_output, edited_output)

		return scores
