from __future__ import annotations

import json
from difflib import SequenceMatcher
from typing import Any


class RelevanceScorer:
	"""Lightweight relevance proxy based on shape and value similarity."""

	_PLACEHOLDER_STRINGS = {
		"string",
		"non-empty string",
		"percentage",
		"channel",
	}

	def _collect_scalars(self, value: Any) -> list[Any]:
		if isinstance(value, dict):
			items: list[Any] = []
			for child in value.values():
				items.extend(self._collect_scalars(child))
			return items
		if isinstance(value, list):
			items = []
			for child in value:
				items.extend(self._collect_scalars(child))
			return items
		return [value]

	def _is_shape_template(self, expected: dict[str, Any]) -> bool:
		scalars = self._collect_scalars(expected)
		if not scalars:
			return False

		placeholder_hits = 0
		for scalar in scalars:
			if isinstance(scalar, str) and scalar.strip().lower() in self._PLACEHOLDER_STRINGS:
				placeholder_hits += 1

		ratio = placeholder_hits / len(scalars)
		return ratio >= 0.35

	def score(self, actual: dict[str, Any], expected: dict[str, Any]) -> float:
		if not actual or not expected:
			return 0.0

		expected_keys = set(expected.keys())
		actual_keys = set(actual.keys())
		if not expected_keys:
			return 0.0

		key_overlap = len(expected_keys & actual_keys) / len(expected_keys)

		if self._is_shape_template(expected):
			# Template fixtures define structure, not exact values.
			return max(0.0, min(1.0, round(key_overlap, 4)))

		expected_text = json.dumps(expected, sort_keys=True)
		actual_text = json.dumps(actual, sort_keys=True)
		value_similarity = SequenceMatcher(None, expected_text, actual_text).ratio()

		# Heavier weight on structural overlap, lighter on string similarity.
		score = (0.7 * key_overlap) + (0.3 * value_similarity)
		return max(0.0, min(1.0, round(score, 4)))
