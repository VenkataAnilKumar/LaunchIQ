from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError


class SchemaComplianceScorer:
	"""Schema compliance metric with partial score fallback on validation errors."""

	def score(self, output: dict[str, Any], schema_class: type[BaseModel] | None) -> float:
		if schema_class is None:
			return 0.0

		try:
			schema_class(**output)
			return 1.0
		except ValidationError as exc:
			top_level_fields = set(schema_class.model_fields.keys())
			if not top_level_fields:
				return 0.0

			invalid_fields: set[str] = set()
			for error in exc.errors():
				loc = error.get("loc", ())
				if loc and isinstance(loc[0], str):
					invalid_fields.add(loc[0])

			valid_count = max(0, len(top_level_fields) - len(invalid_fields))
			partial = valid_count / len(top_level_fields)
			return max(0.0, min(1.0, round(partial, 4)))
