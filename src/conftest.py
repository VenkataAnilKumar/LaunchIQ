"""Test defaults: never touch real LLM/search APIs, and use a throwaway SQLite DB.

These must be set before any ``src.*`` module reads settings (settings are cached and
the DB engine is created at import time), hence at conftest import.
"""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="launchiq-test-")

os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("SEARCH_PROVIDER", "fake")
os.environ.setdefault("TASK_RUNNER", "inline")
os.environ.setdefault("AUTO_CREATE_TABLES", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_tmp}/test.db")
os.environ.setdefault("INTEGRATION_ENCRYPTION_KEY", "test-only-encryption-key-not-secret")
