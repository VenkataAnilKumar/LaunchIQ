from __future__ import annotations

from typing import Any


def _flatten_leaves(value: Any, prefix: str = "") -> dict[str, Any]:
	if isinstance(value, dict):
		out: dict[str, Any] = {}
		for key, child in value.items():
			path = f"{prefix}.{key}" if prefix else str(key)
			out.update(_flatten_leaves(child, path))
		return out
	if isinstance(value, list):
		out = {}
		for idx, child in enumerate(value):
			path = f"{prefix}[{idx}]"
			out.update(_flatten_leaves(child, path))
		return out
	return {prefix: value}


class EditRateScorer:
	"""Fraction of fields changed between original and edited outputs."""

	def score(self, original: dict[str, Any], edited: dict[str, Any]) -> float:
		if not original and not edited:
			return 0.0

		original_flat = _flatten_leaves(original)
		edited_flat = _flatten_leaves(edited)

		all_paths = set(original_flat.keys()) | set(edited_flat.keys())
		if not all_paths:
			return 0.0

		changed = 0
		for path in all_paths:
			if original_flat.get(path) != edited_flat.get(path):
				changed += 1

		rate = changed / len(all_paths)
		return max(0.0, min(1.0, round(rate, 4)))
