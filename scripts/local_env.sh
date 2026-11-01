#!/usr/bin/env bash
# Source this to run LaunchIQ locally with no API keys, no Docker, no Postgres:
#   fake LLM + fake web search + SQLite + local Redis.
export LLM_PROVIDER="${LLM_PROVIDER:-fake}"
export SEARCH_PROVIDER="${SEARCH_PROVIDER:-fake}"
export DATABASE_URL="sqlite+aiosqlite:///${PWD}/.local/launchiq.db"
export AUTO_CREATE_TABLES=true
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export TASK_RUNNER="${TASK_RUNNER:-inline}"
export INTEGRATION_ENCRYPTION_KEY="${INTEGRATION_ENCRYPTION_KEY:-local-dev-only-key}"
export APP_ENV=development
