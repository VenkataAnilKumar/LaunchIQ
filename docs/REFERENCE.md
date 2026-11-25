# Reference

Setup routes, the HTTP API, configuration and the evaluation tools.

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 22+ and pnpm 9+
- Docker + Docker Compose
- Anthropic API key ([get one here](https://console.anthropic.com))

### Clone and Run

```bash
# 1. Clone
git clone https://github.com/venkataanilkumar/launchiq.git
cd launchiq

# 2. Configure environment
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY at minimum

# 3. Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# 4. Run database migrations
make migrate

# 5. (optional) add a finished sample launch for your user
make seed USER_ID=<your Clerk user id>     # defaults to local-dev-user

# 6. Start everything
make dev
```

Open **http://localhost:3000**. Sign-in uses Clerk, so set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` in `.env`
(the keyless route below needs neither Clerk nor Docker). This Docker route has not been verified end to end; the keyless one has.

### Try it with no API keys, Docker or Postgres

The whole product runs locally against a deterministic **fake LLM**, fake web search, SQLite and a local Redis
(`redis-server` must be installed). Output is canned, so this verifies the product flow, not model quality.

```bash
pip install -r src/apps/api/requirements.txt
make local                       # API on :8000 (source scripts/local_env.sh for the same env)
cd src/apps/web && pnpm install
NEXT_PUBLIC_DEV_BEARER_TOKEN=$(python3 ../../../scripts/dev_token.py) pnpm dev   # http://localhost:3000
```

`make local-celery` runs the same stack with a real Celery worker; `make local-down` stops it.
Set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` (and `SEARCH_PROVIDER=tavily`, `TAVILY_API_KEY`)
for real runs. Browser E2E scripts live in `scripts/e2e/`.

### Minimal `.env` to get started

```bash
ANTHROPIC_API_KEY=sk-ant-...        # Required — everything else is optional

TAVILY_API_KEY=tvly-...             # Enables real web search (market intelligence)
LANGFUSE_PUBLIC_KEY=pk-lf-...       # Enables agent observability dashboard
```

See [`.env.example`](../.env.example) for the complete reference with all 20+ variables.

### Makefile Commands

```bash
make dev        # Start API + Celery worker + Next.js (all in one)
make test       # pytest src/ with coverage
make local      # keyless local stack (fake LLM + SQLite + local Redis)
make eval       # offline eval gate over the brief corpus (no keys)
make eval-live  # same corpus against the real API (needs ANTHROPIC_API_KEY)
make migrate    # Run Alembic migrations
make seed       # Load a finished sample launch (USER_ID=... to choose the owner)
make demo       # migrate + seed + dev (Docker route)
```


## API Overview

All routes are under `/api/v1` and need a bearer token, except health. Interactive docs are at `/docs` outside production.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/launches` | Create a launch and start the pipeline |
| GET | `/launches` | List your launches |
| GET | `/launches/{id}` | Detail: status, formatted sections, per-agent runs, cost, pending review |
| GET | `/launches/{id}/stream` | Live progress events (SSE) |
| GET | `/launches/{id}/export?format=md\|json` | The finished launch document |
| POST | `/launches/{id}/analytics` | Recommendations from metrics you supply (launch must be completed) |
| GET | `/hitl/{id}/pending` | The review waiting for you |
| POST | `/hitl/{id}/decide` | Approve, edit or reject (optional `checkpoint` guards against stale clicks) |
| GET | `/agents/{id}` | Per-agent status |
| POST | `/agents/{id}/{agent}/retry` | Re-run a failed agent and resume |
| GET | `/schemas/{agent}` | JSON Schema of an agent's output (used to build edit forms) |
| POST / DELETE | `/integrations/{hubspot\|slack\|ga4}` | Store or remove credentials (preview; not used by the pipeline yet) |
| GET | `/health`, `/health/ready` | Health checks (no auth) |


## Configuration

Set in `.env` (see [`.env.example`](../.env.example)). The keyless local stack sets the offline values for you.

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_PROVIDER` | `anthropic` | `anthropic` for the real API, `fake` for the offline model |
| `ANTHROPIC_API_KEY` | — | Required when `LLM_PROVIDER=anthropic` |
| `ANTHROPIC_MODEL_OPUS` / `_SONNET` / `_HAIKU` | `claude-opus-4-6` / `claude-sonnet-4-6` / `claude-haiku-4-5-20251001` | Model IDs per tier (defaults not yet checked against a live account) |
| `SEARCH_PROVIDER`, `TAVILY_API_KEY` | `tavily` | Web search, or `fake` for canned results |
| `LAUNCH_COST_BUDGET_USD` | `5.0` | Stops a launch when its estimated cost passes this; `0` disables |
| `DATABASE_URL` | PostgreSQL (asyncpg) | Use `sqlite+aiosqlite:///...` for local runs |
| `AUTO_CREATE_TABLES` | `false` | Create tables on startup (local only; production uses Alembic) |
| `REDIS_URL` | `redis://localhost:6379/0` | Events, rate limiting, Celery broker |
| `TASK_RUNNER` | `celery` | `inline` runs the pipeline inside the API process |
| `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW` | `300` / `60` | Per-IP requests per window |
| `CLERK_SECRET_KEY`, `CLERK_JWT_AUDIENCE`, `INTEGRATION_ENCRYPTION_KEY` | — | Sign-in and encrypted integration credentials |
| `SENTRY_DSN`, `LANGFUSE_PUBLIC_KEY` / `_SECRET_KEY` | — | Optional observability |
| Web: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `API_URL`, `NEXT_PUBLIC_DEV_BEARER_TOKEN` | — / `http://localhost:8000` / — | Sign-in, API proxy target, keyless local session (never set the dev token in production) |


## Evals

`make eval` runs the **real agents** over a 16-brief corpus (`src/evals/corpus/briefs.json`: diverse products plus
prompt-injection briefs) against the fake LLM and gates on schema compliance, hallucination heuristics, error rate,
source grounding (citations must come from actual search results), product mention and injection leakage. It runs
in CI on every PR with no secrets. It verifies plumbing and safety behaviour, **not model quality**.

`make eval-live` runs the same corpus against the real API and also reports tokens and cost per agent.
No live run has been recorded yet, so the `live` thresholds in `src/evals/regression/baseline.json` are
unmeasured targets; run `python src/evals/regression/update_baseline.py` with a key, review, and commit to replace them.

