"""Test defaults: never touch real LLM/search APIs from the unit-test suite."""
import os

os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("SEARCH_PROVIDER", "fake")
