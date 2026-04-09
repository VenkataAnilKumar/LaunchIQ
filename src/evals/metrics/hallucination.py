from __future__ import annotations

import json
import re
from typing import Any


class HallucinationScorer:
	"""Heuristic hallucination detector aligned with OutputValidator signals."""

	_HALLUCINATION_PATTERNS = (
		r"\bas of \d{4}\b",
		r"\bI don't have access\b",
		r"\bI cannot browse\b",
		r"\bmy training data\b",
	)

	def score(self, output: dict[str, Any], context: dict[str, Any] | None = None) -> float:
		if not output:
			return 1.0

		text_blob = json.dumps(output, ensure_ascii=True)
		flags = 0
		for pattern in self._HALLUCINATION_PATTERNS:
			flags += len(re.findall(pattern, text_blob, re.IGNORECASE))

		# Optional weak grounding check: severe penalty if context is non-empty and output is tiny.
		if context and len(text_blob) < 40:
			flags += 1

		rate = flags / max(1, len(self._HALLUCINATION_PATTERNS))
		return max(0.0, min(1.0, round(rate, 4)))
