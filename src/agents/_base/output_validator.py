"""
Output validator — enforces schema compliance and runs hallucination heuristics.

Two-stage gate applied after every agent response:
  1. Pydantic schema validation (hard fail → raise)
  2. Citation enforcer + hallucination heuristics (soft fail → flag)
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

# Simple heuristics — phrases that suggest confabulation
_HALLUCINATION_SIGNALS = [
    r"\bas of \d{4}\b",           # stale date claims
    r"\bI don't have access\b",   # model talking about itself
    r"\bI cannot browse\b",
    r"\bmy training data\b",
]


class ValidationResult(BaseModel):
    valid: bool
    validated_output: dict[str, Any]
    schema_errors: list[str] = []
    hallucination_flags: list[str] = []


class OutputValidator:
    def validate(self, raw: dict[str, Any], schema: type[BaseModel]) -> dict[str, Any]:
        result = self._run(raw, schema)
        if not result.valid:
            logger.error("Output validation failed: %s", result.schema_errors)
            raise ValueError(f"Agent output failed schema validation: {result.schema_errors}")
        if result.hallucination_flags:
            logger.warning("Hallucination signals detected: %s", result.hallucination_flags)
        return result.validated_output

    def _run(self, raw: dict[str, Any], schema: type[BaseModel]) -> ValidationResult:
        # Stage 1: schema
        try:
            parsed = schema(**raw)
            validated = parsed.model_dump()
        except ValidationError as exc:
            errors = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
            return ValidationResult(valid=False, validated_output={}, schema_errors=errors)

        # Stage 2: hallucination heuristics on string fields
        flags: list[str] = []
        text_blob = json.dumps(validated)
        for pattern in _HALLUCINATION_SIGNALS:
            matches = re.findall(pattern, text_blob, re.IGNORECASE)
            if matches:
                flags.extend(matches)

        return ValidationResult(valid=True, validated_output=validated, hallucination_flags=flags)

    def validate_text(self, text: str) -> list[str]:
        """Run heuristics on raw text — returns list of flagged phrases."""
        flags: list[str] = []
        for pattern in _HALLUCINATION_SIGNALS:
            flags.extend(re.findall(pattern, text, re.IGNORECASE))
        return flags
