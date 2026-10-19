"""Unit tests for OutputValidator hallucination heuristics and severity."""
from __future__ import annotations

import pytest
from pydantic import BaseModel

from src.agents._base.output_validator import OutputValidator, ValidationResult


class DummySchema(BaseModel):
    text: str
    score: float = 0.5


def test_validate_passes_clean_output():
    validator = OutputValidator()
    raw = {"text": "This is a solid product launch plan.", "score": 0.8}
    out = validator.validate(raw, DummySchema)
    assert out["text"] == raw["text"]
    assert out["score"] == 0.8


def test_validate_raises_on_schema_error():
    validator = OutputValidator()
    raw_bad = {"text": 123}  # type error
    with pytest.raises(ValueError, match="schema validation"):
        validator.validate(raw_bad, DummySchema)


def test_hallucination_flags_and_severity():
    validator = OutputValidator()
    raw = {
        "text": "As of 2020 this always works. According to studies it is 100% guaranteed exact figure.",
        "score": 0.1,
    }
    result = validator._run(raw, DummySchema)
    assert result.valid is True
    assert len(result.hallucination_flags) >= 3
    assert result.severity == "high"
    assert any("always" in f.lower() for f in result.hallucination_flags)


def test_validate_text_flags_signals():
    validator = OutputValidator()
    flags = validator.validate_text("I don't have access to my training data as of 2023.")
    assert len(flags) >= 2


def test_severity_low_medium():
    validator = OutputValidator()
    # one signal
    raw_low = {"text": "This is always the case.", "score": 0.5}
    res_low = validator._run(raw_low, DummySchema)
    assert res_low.severity == "low"

    # two signals
    raw_med = {"text": "Always 100% accurate according to research.", "score": 0.5}
    res_med = validator._run(raw_med, DummySchema)
    assert res_med.severity == "medium"
