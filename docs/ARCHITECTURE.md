# Architecture

How LaunchIQ is put together: the agent pipeline, key features, the full tech stack, the project layout and the reasoning behind the main design decisions. For what runs today versus what is planned, see [ROADMAP.md](ROADMAP.md).

## The problem it targets

> *"We spent 6 weeks on launch prep. Hired 3 agencies. Still missed our ICP."*

Product launches fail not because of bad products — but because teams lack the intelligence to launch precisely.

- Market research takes **weeks** and costs **thousands**
- Persona development is **guesswork** without real data
- Launch strategies are **copy-pasted templates**
- Content is written by committees with **no signal from the market**

**LaunchIQ turns a short brief into market research, personas, a 90-day launch strategy and launch content, with a human review at two checkpoints.** (Run time and cost per launch have not been measured with a real model yet; see [Project Status](ROADMAP.md#project-status).)

## The Agent Pipeline

```
  Your Product Brief
         │
         ▼
╔════════════════════════════════════════════════════════════════╗
║                    ORCHESTRATOR                                ║
║      Plain control flow — it makes no model calls itself       ║
║  Runs agents in order · saves state · pauses at HITL reviews   ║
╚══════╤═════════════════════════════════════════╤══════════════╝
       │                                         │
       ▼                                         ▼
┌──────────────────┐               ┌──────────────────────┐
│ MARKET           │               │ AUDIENCE INSIGHT     │
│ INTELLIGENCE     │──────────────▶│                      │
│                  │               │ Personas             │
│ Tavily search    │               │ Messaging framework  │
│ Competitors      │               │ Channel picks        │
│ Trends + sources │               │ Sonnet-tier model    │
│ Sonnet-tier      │               └──────────┬───────────┘
└──────────────────┘                          │
       ⚡ HITL: brief_review                  │
                              ┌───────────────▼───────────────┐
                              │       LAUNCH STRATEGY         │
                              │                               │
                              │  Phased plan                  │
                              │  Channels · budget · risks    │
                              │  Opus-tier + extended thinking│
                              └───────────────┬───────────────┘
                                    ⚡ HITL: strategy_review
                    ┌───────────────────────────────────────────┐
                    │          CONTENT GENERATION               │
                    │                                           │
                    │  Email Sequence · Social Posts · Ad Copy  │
                    │  A/B variants                             │
                    │  Three streams generated concurrently     │
                    │  Sonnet-tier model                        │
                    └───────────────────┬───────────────────────┘
                                        │
                              ┌─────────▼──────────┐
                              │  Launch document   │
                              │  (export: Markdown)│
                              └─────────┬──────────┘
                                        │  later, on demand
                    ┌───────────────────▼───────────────────────┐
                    │        ANALYTICS & FEEDBACK               │
                    │  Recommendations from metrics you supply  │
                    │  Haiku-tier model (GA4 connector: planned)│
                    └───────────────────────────────────────────┘
```

Model tiers (Opus / Sonnet / Haiku) resolve to model IDs from settings (`ANTHROPIC_MODEL_OPUS` / `_SONNET` / `_HAIKU`), so
they can be changed without code edits. The defaults have not been checked against a live account.

> **HITL (Human-in-the-Loop)** is a structural pipeline gate — not a UX feature. At a checkpoint the orchestrator stores the pending review in the database and *stops* (no worker is held while waiting). A decision arriving via `POST /api/v1/hitl/{id}/decide` is saved, schema-validated if it carries edits, and enqueues a resume that skips every agent that already finished. Resume from anywhere: browser, mobile, Slack, CLI.


## Key Features

| Feature | What it means |
|---------|--------------|
| **Multi-Agent Pipeline** | Orchestrator + 4 pipeline agents (market, audience, strategy, content) + an on-demand post-launch analytics agent. Each has a Lambda-style handler; the deployed topology is not verified |
| **Extended Thinking** | The strategy agent is configured to use extended thinking on an Opus-tier model (not yet run against the real API) |
| **Live Progress** | Server-Sent Events show each agent starting, finishing and needing review, with tokens and estimated cost |
| **Structural HITL** | Pipeline pauses at two review checkpoints. Approve, edit (schema-validated) or reject; stale clicks get a 409 instead of approving the next review blind |
| **Tool Executors** | Web search (Tavily) is used by the market agent. HubSpot, Slack and GA4 executors exist behind an MCP-style interface but are not wired into the pipeline yet |
| **Eval Gate in CI** | Every PR runs the real agents over a brief corpus (fake LLM) and gates on schema, grounding, injection and error regressions |
| **Memory** | PostgreSQL/SQLite (launches, agent runs, HITL records) + Redis (events, rate limiting) |
| **Parallel Content** | Email, social and ads are generated concurrently |
| **A/B by Default** | Every content piece ships in two variants, automatically |
| **Grounded & Guarded** | Trend sources must be URLs the agent actually got from search; every prompt treats briefs, web pages and human edits as data, not instructions; per-launch cost budget |


## Tech Stack

### AI & Agents

| Component | Technology | Role |
|-----------|-----------|------|
| Agent Framework | Anthropic Claude SDK (native) | Orchestration + tool use |
| Orchestrator | Plain Python (no model calls) | Ordering, persistence, review checkpoints, cost budget |
| Market + Audience + Content | Sonnet-tier model | Balanced capability + cost |
| Strategy | Opus-tier model + extended thinking | Deeper reasoning where it matters |
| Analytics | Haiku-tier model | Cost-optimized feedback |
| Tools | MCP-style executor interface | Tavily search is wired; others are not yet |
| Reliability | ReAct tool loop · schema validation with one repair retry · retries and backoff · per-launch cost budget | Keeps bad output and failures from reaching users |
| Offline mode | Deterministic fake model (`LLM_PROVIDER=fake`) | Runs and tests the whole product with no API key |

### Backend

Versions are the minimums declared in `src/apps/api/requirements.txt`; CI runs Python 3.12.

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI 0.115+ on Python 3.12+ (async throughout), Uvicorn |
| Validation & settings | Pydantic v2, pydantic-settings |
| Task Queue | Celery 5.x with a Redis broker, or an inline runner for local runs |
| Database | PostgreSQL 16 (Docker image) via SQLAlchemy 2.x async + asyncpg; SQLite (aiosqlite) for keyless local runs |
| Migrations | Alembic (001 initial schema, 002 agent-run cost; verified on SQLite) |
| Cache / Pub-Sub | Redis 7 — SSE events, rate limiting, Celery broker |
| Auth | Clerk JWTs verified with python-jose in production; unsigned dev tokens are accepted only outside production, for local use |
| HTTP client | httpx (Tavily, integration checks) |
| Observability | Sentry (when `SENTRY_DSN` is set); optional Langfuse client for evals |

### Frontend

Versions are those declared in `src/apps/web/package.json`.

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 15.3 — App Router, TypeScript 5.7+ |
| UI Runtime | React 19 |
| Styling | Custom CSS design system (Tailwind v4's reset is loaded; components are hand-built) |
| Server State | TanStack Query 5 |
| Client State | Zustand 5 |
| Auth | Clerk 6; a dev-token session for keyless local use |
| Real-time | Server-Sent Events read with `fetch` (so the auth header can be sent) |
| Forms | Plain controlled forms; review edit forms are generated from each agent's JSON Schema with `@rjsf/core` 6 |
| Documents | `react-markdown` 10 + `remark-gfm` |
| UI details | Lucide icons, Sonner toasts, one Radix dialog |
| Types | Hand-written in `src/packages/types` |

> `package.json` still lists a few packages nothing imports (`react-hook-form`, `zod`, `@hookform/resolvers`,
> `@uiw/react-json-view`, `nuqs`, `class-variance-authority`, `@radix-ui/react-tabs`); they are candidates for removal.

### Testing & Quality

| What | Tool | Notes |
|------|------|-------|
| Python tests | pytest + pytest-asyncio | About 70 tests: agents, orchestrator, validators, API integration on SQLite with the fake model |
| Offline eval gate | `run_regression.py --offline` | The real agents over 16 briefs incl. prompt-injection cases; runs on every PR with no secrets |
| Live evals | `run_regression.py` | Same corpus against the real API; needs a key; no baseline recorded yet |
| Browser E2E | Playwright (Chromium) | `scripts/e2e/`: full flow, reject path, edge cases, failure screen |
| Lint / types | ruff; ESLint + `tsc` | Run in CI on every PR |
| CI | GitHub Actions | `pr.yml` (lint, type check, unit tests, eval gate) and `integration.yml` (end-to-end pipeline test) |

### Infrastructure & Observability

> **Designed, not deployed.** Only Sentry (when `SENTRY_DSN` is set) and the optional Langfuse eval client are in the code today. LangSmith, PostHog and the AWS/Vercel deployments below are planned and unverified.

| Component | Technology |
|-----------|-----------|
| Frontend Hosting | Vercel — Edge Network + ISR |
| API Hosting | AWS ECS Fargate — rolling deploys |
| Agent Hosting | AWS Lambda — one function per agent, 300s timeout |
| Infrastructure as Code | AWS CDK v2 (Python) |
| Tracing | LangSmith — agent traces, tool call logs |
| Evals | Langfuse — per-agent scores, regression tracking |
| Errors | Sentry |
| Product Analytics | PostHog |
| CI/CD | GitHub Actions — lint → typecheck → test → eval gate → deploy |


## Architecture Decisions

<details>
<summary><strong>Planned: one Lambda per agent instead of a monolith</strong> (today the agents run inside the API/worker process)</summary>
<br/>
Each agent is independently deployable, scalable, and observable. A slow content generation run doesn't block a market intelligence run. Agents can be hot-swapped — update a prompt, redeploy one Lambda, zero downtime. Provisioned concurrency on the orchestrator eliminates cold starts on the critical path.
</details>

<details>
<summary><strong>Why HITL as a pipeline gate, not a UX feature?</strong></summary>
<br/>
HITL is implemented at the orchestrator level — the run ends at a checkpoint and the pending review lives in the database until a human decision arrives via <code>POST /api/v1/hitl/{id}/decide</code>, which then enqueues a resume. This means the guarantee is structural and survives worker restarts. The frontend being closed, refreshed, or on a different device doesn't matter. Resume from anywhere: browser, mobile, Slack bot, CLI.
</details>

<details>
<summary><strong>Why an eval gate in CI instead of just unit tests?</strong></summary>
<br/>
LLM outputs are non-deterministic, and unit tests with one mocked answer don't exercise the real agent code. The PR gate runs the real agents over a 16-brief corpus (including prompt-injection briefs) against a deterministic fake model and fails on schema, grounding, injection-leak or error regressions. It checks plumbing and safety behaviour, not model quality; a scheduled live run against the real API is meant to measure quality, but no live baseline has been recorded yet.
</details>

<details>
<summary><strong>Why MCP tool servers instead of direct API calls?</strong></summary>
<br/>
Each tool executor is self-contained with its own credentials and schema validation, behind an MCP-style interface. Agents declare which tools they need and the tool loop handles execution, so swapping Tavily for another search provider changes one file. (Only the Tavily executor is wired into the pipeline today.)
</details>

<details>
<summary><strong>Why split memory between PostgreSQL and Redis?</strong></summary>
<br/>
Redis handles SSE pub/sub, rate limiting and the Celery broker, where latency matters. PostgreSQL holds launch records, agent runs and HITL decisions, where durability matters. A vector store (for semantic search over past reports and personas) is a possible later addition once there is data worth retrieving; it was removed until then rather than left half-wired.
</details>


## Project Structure

```
launchiq/
│
├── src/
│   ├── agents/                     # Orchestrator + 5 agents (Lambda-style handlers)
│   │   ├── _base/                  # BaseAgent · CognitiveLoop · LLM client + fake · OutputValidator
│   │   ├── orchestrator/           # Resumable pipeline: run store · dispatcher · synthesizer
│   │   ├── market_intelligence/    # Web research + competitor analysis (sources must come from search)
│   │   ├── audience_insight/       # Personas + messaging framework
│   │   ├── launch_strategy/        # 90-day phased launch plan
│   │   ├── content_generation/     # Email · social · ads (concurrent)
│   │   └── analytics_feedback/     # Recommendations from supplied metrics
│   │
│   ├── apps/
│   │   ├── api/                    # FastAPI backend
│   │   │   ├── middleware/         # Auth · PII scrubber · rate limit · security headers
│   │   │   ├── routers/            # launches · agents · hitl · schemas · integrations · health
│   │   │   ├── services/           # launch · agent · stream · hitl
│   │   │   └── workers/            # Celery tasks + inline runner
│   │   └── web/                    # Next.js 15 frontend
│   │       ├── app/                # Landing · dashboard · new launch · launch workspace (tabs) · settings
│   │       ├── components/         # agents/ · hitl/ · launch/ · ui/ · auth/
│   │       ├── store/              # Zustand stores
│   │       └── lib/                # api client · SSE hook · schema helpers · samples
│   │
│   ├── tools/                      # Tool executors (MCP-style interface)
│   │   ├── tavily_search/          # Web research (wired)
│   │   ├── hubspot/ · slack/ · ga4/ · internal/   # present, not wired into the pipeline
│   │
│   ├── memory/
│   │   ├── short_term/             # Redis — events (pub/sub) · session store
│   │   └── structured/             # SQL — launches · agent runs · users · HITL records · migrations
│   │
│   ├── evals/                      # Eval corpus + evaluator + regression gate
│   │   ├── corpus/                 # 16 briefs incl. prompt-injection cases
│   │   ├── framework/              # Evaluator · Langfuse client
│   │   ├── metrics/                # hallucination · schema · grounding
│   │   └── regression/             # run_regression.py · baseline.json · update_baseline.py
│   │
│   └── infra/                      # AWS CDK stacks + Dockerfiles (designed, not deployed)
│
├── docs/
│   ├── demo/                       # Demo walkthrough + screenshots
│   ├── 01_Product_Thinking/        # PRD · Research · Competitive · GTM · Business Model
│   ├── 02_Technical_Feasibility/   # Architecture · Security · Implementation Plan
│   ├── 03_AI_Architecture/         # Agent Matrix · Data Flow · Agentic AI 2026
│   ├── portfolio/                  # Case study and portfolio pages
│   └── DEPLOYMENT.md
│
├── scripts/                        # Local stack · dev token · browser E2E tests
├── .github/workflows/              # pr · integration · deploy-staging · deploy-production · eval-scheduled
├── docker-compose.yml              # PostgreSQL + Redis
├── pyproject.toml · poetry.lock    # Python project settings and locked dependencies
├── pnpm-workspace.yaml             # Node workspace
└── Makefile                        # local · dev · test · eval · migrate · seed · demo
```

