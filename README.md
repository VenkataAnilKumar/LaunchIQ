<div align="center">

<img src="docs/assets/launchiq-logo.svg" alt="LaunchIQ" width="100" height="100" />

# LaunchIQ

### AI-Powered Product Launch Intelligence

*Turn a product brief into a researched, human-reviewed launch plan.*

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude-D97706?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![CI](https://img.shields.io/github/actions/workflow/status/venkataanilkumar/launchiq/pr.yml?style=for-the-badge&label=CI&logo=githubactions&logoColor=white)](https://github.com/venkataanilkumar/launchiq/actions)

<br/>

[**Demo**](docs/demo/README.md) · [**Documentation**](docs/) · [**Architecture**](docs/03_AI_Architecture/04_Agentic_AI_Architecture.md) · [**Portfolio**](docs/portfolio/03_Case_Study.md)

⭐ If LaunchIQ helps your team, please star this repository to support the project.

<br/>

<img src="docs/demo/screenshots/04-review-market.webp" alt="LaunchIQ review step: formatted market research with Approve, Edit and Reject (fake-model demo data)" width="100%"/>

</div>

---

## The Problem

> *"We spent 6 weeks on launch prep. Hired 3 agencies. Still missed our ICP."*

Product launches fail not because of bad products — but because teams lack the intelligence to launch precisely.

- Market research takes **weeks** and costs **thousands**
- Persona development is **guesswork** without real data
- Launch strategies are **copy-pasted templates**
- Content is written by committees with **no signal from the market**

**LaunchIQ turns a short brief into market research, personas, a 90-day launch strategy and launch content, with a human review at two checkpoints.** (Run time and cost per launch have not been measured with a real model yet; see [Project Status](#project-status).)

---

## What It Does

<table>
<tr>
<td width="50%" valign="top">

**You provide:**
- Product name + description
- Target market
- Known competitors *(optional)*

</td>
<td width="50%" valign="top">

**LaunchIQ delivers:**
- Market intelligence report with competitor breakdown
- Buyer personas with messaging hooks
- 90-day phased launch strategy
- Full content bundle — email, social, ads (A/B variants)
- Post-launch recommendations from the metrics *you* measure
- One launch document you can read, copy and download as Markdown

</td>
</tr>
</table>

---

## Demo

There is no hosted demo yet; the demo runs on your computer with a fake model (no API keys), so the generated text
is placeholder content. The full 6-minute walkthrough, with exact inputs and expected results, is in
**[`docs/demo/`](docs/demo/README.md)**.

| | |
|---|---|
| ![Landing](docs/demo/screenshots/01-landing.webp) | ![Review](docs/demo/screenshots/05-review-strategy.webp) |
| **Landing** with a one-click sample brief | **Human review** of the launch strategy |
| ![Edit](docs/demo/screenshots/06-edit-form-generated-from-schema.webp) | ![Document](docs/demo/screenshots/11-results-document.webp) |
| **Edit** form generated from the agent's schema | **Document** view, copy and Markdown download |

```bash
make local        # API with the fake model
source scripts/local_env.sh && python3 src/data/seed.py --demo --user-id local-dev-user
cd src/apps/web && pnpm install && NEXT_PUBLIC_DEV_BEARER_TOKEN=$(python3 ../../../scripts/dev_token.py) pnpm dev   # http://localhost:3000
```

---

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

---

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

---

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

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI 0.115 + Python 3.12 (async throughout) |
| Task Queue | Celery 5.4 + Redis broker |
| Database | PostgreSQL 16 via SQLAlchemy 2.x (async) |
| Cache / Pub-Sub | Redis 7 — SSE events, rate limiting, Celery broker |
| Auth | Clerk — JWT, OAuth, magic links |
| Migrations | Alembic |

### Frontend

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 15 — App Router |
| UI Runtime | React 19 |
| Styling | Custom CSS design system (Tailwind v4's reset is loaded; components are hand-built) |
| Server State | TanStack Query v5 |
| Client State | Zustand v5 |
| Real-time | Server-Sent Events read with `fetch` (so the auth header can be sent) |
| Forms | Plain controlled forms; review edit forms are generated from each agent's JSON Schema with `@rjsf/core` |
| Documents | `react-markdown` + `remark-gfm` for the launch document |
| Types | Hand-written in `src/packages/types` |

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

---

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

---

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

See [`.env.example`](.env.example) for the complete reference with all 20+ variables.

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

---

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

---

## Documentation

| Document | Description |
|----------|-------------|
| [PRD](docs/01_Product_Thinking/01_PRD.md) | Problem statement, personas, user stories, success metrics |
| [User Research](docs/01_Product_Thinking/02_User_Research_Summary.md) | Research methodology, insights, pain points |
| [Competitive Analysis](docs/01_Product_Thinking/03_Competitive_Analysis.md) | 5-competitor breakdown + differentiation matrix |
| [GTM Strategy](docs/01_Product_Thinking/05_GTM_Strategy.md) | Channels, pricing tiers, launch phases |
| [Business Model Canvas](docs/01_Product_Thinking/06_Business_Model_Canvas.md) | All 9 blocks + unit economics |
| [Demo walkthrough](docs/demo/README.md) | Run it yourself in 6 minutes, with exact inputs and screenshots |
| [Technical Architecture](docs/02_Technical_Feasibility/01_Technical_Architecture.md) | 13-layer system architecture |
| [Security & Compliance](docs/02_Technical_Feasibility/05_Security_Compliance.md) | OWASP, GDPR, CCPA, SOC2 readiness |
| [E2E Product Architecture](docs/02_Technical_Feasibility/06_End_to_End_Product_Architecture.md) | Request flow, scalability, cost model |
| [Implementation Plan](docs/02_Technical_Feasibility/08_Implementation_Plan.md) | Phase-by-phase build guide |
| [Agent Capability Matrix](docs/03_AI_Architecture/01_Agent_Capability_Matrix.md) | Per-agent tools, models, inputs, outputs |
| [Data Flow Diagram](docs/03_AI_Architecture/02_Data_Flow_Diagram.md) | End-to-end data movement across all layers |
| [Agentic AI Architecture](docs/03_AI_Architecture/04_Agentic_AI_Architecture.md) | 2026 patterns: Anthropic · OpenAI · AWS · Azure · Google |

---

## Evals

`make eval` runs the **real agents** over a 16-brief corpus (`src/evals/corpus/briefs.json`: diverse products plus
prompt-injection briefs) against the fake LLM and gates on schema compliance, hallucination heuristics, error rate,
source grounding (citations must come from actual search results), product mention and injection leakage. It runs
in CI on every PR with no secrets. It verifies plumbing and safety behaviour, **not model quality**.

`make eval-live` runs the same corpus against the real API and also reports tokens and cost per agent.
No live run has been recorded yet, so the `live` thresholds in `src/evals/regression/baseline.json` are
unmeasured targets; run `python src/evals/regression/update_baseline.py` with a key, review, and commit to replace them.

---

## Project Status

**Verified end to end (fake LLM, SQLite, local Redis, Celery or inline runner; 62 unit/API tests, browser E2E in Chromium):**
landing page → sample brief → create launch → live agent progress → formatted review checkpoint → read results mid-pause → approve / edit (form generated from the agent's schema) / reject → completed brief → document view and Markdown export → post-launch analytics from supplied metrics; dashboard search and filters; mobile layout; per-user isolation; failed-agent retry; cost budget.

**Not verified yet:** real Claude/Tavily runs (no live eval baseline recorded), PostgreSQL, Docker Compose, AWS CDK/Lambda/ECS and Vercel deploys, HubSpot/Slack integrations, Clerk in production.
**Not built:** GA4 connector, vector memory/RAG, billing, onboarding.

---

## Production Readiness (planned, not built)

Not everything below is needed for every use. What is required depends on the goal:

| Goal | Auth + security pass | Hosting | Billing + onboarding |
|------|----------------------|---------|----------------------|
| Private / portfolio demo (run locally) | not needed | not needed | not needed |
| Public demo anyone can try | **required** (real Clerk login, API in production mode) | **required** (one simple host) | skip |
| Charging customers | required | required | required |

Notes:
- The local dev login accepts unsigned tokens, so it must never be used on a public server.
- Every launch costs real model spend. A public demo also needs a per-user launch cap (the per-launch cost budget already exists).
- Error tracking (Sentry is wired in) is enough monitoring at first.

**Reuse instead of building from scratch** (all MIT; patterns to port, not templates to adopt, since none match FastAPI + Next.js + Clerk):
- Stripe Checkout, customer portal and subscription webhooks: [`nextjs/saas-starter`](https://github.com/nextjs/saas-starter) (about 330 lines of TypeScript to port to FastAPI; the `users` table already has a `plan` column).
- Docker Compose, Traefik with automatic HTTPS and deploy-on-merge CI: [`fastapi/full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template) (add Redis and the Celery worker, swap the Vite frontend for Next.js).
- Clerk token verification: replace the hand-written JWKS fetch in `src/apps/api/middleware/auth.py` with Clerk's official verification library.

Rough estimate: about 7-9 days with reuse versus 12-14 from scratch; the minimum for a public demo is about 3-4 days
(live eval baseline, Clerk login, per-user cap, one deploy).

---

## Roadmap

**Done**
- [x] Multi-agent pipeline with resumable human-review checkpoints (DB-backed, event-driven)
- [x] Real-time SSE dashboard (authenticated stream), status banner, retry, export
- [x] Offline eval gate in CI over a 16-brief corpus incl. prompt-injection briefs
- [x] Source grounding, prompt-injection guards, per-launch cost budget
- [x] Post-launch analytics from user-supplied metrics
- [x] Keyless local stack (`make local`)
- [x] A/B content variants by default; extended thinking on the strategy agent

**Next**
- [ ] Live eval baseline (needs `ANTHROPIC_API_KEY`) and real-model prompt tuning
- [ ] Billing, onboarding, production auth (Clerk) and security pass — see Production Readiness (only the parts your goal needs)
- [ ] Hosting, secrets and monitoring for production — see Production Readiness
- [ ] Vector memory (Qdrant) for reuse of past reports/personas, if it proves worth it
- [ ] GA4 connector for analytics

**Later**
- [ ] Slack bot — trigger and approve launches from Slack
- [ ] Brand voice learning — improve content from past launch performance
- [ ] Competitor monitoring — weekly automated market intelligence updates
- [ ] Multi-language content generation
- [ ] White-label API for marketing agencies

---

## For Hiring Managers

This project demonstrates end-to-end production proficiency across:

**AI Engineering**
Multi-agent orchestration · Resumable human-in-the-loop workflows · Tool-use loops (ReAct) with validate-and-repair retries · Prompt-injection defences · Source grounding · Offline eval gate with adversarial cases · Cost budgets · Deterministic fake-model testing

**Backend Engineering**
FastAPI async architecture · SQLAlchemy 2.x async · Celery distributed tasks · Redis pub/sub · JWT auth middleware · Rate limiting · PII scrubbing pipeline · SSE streaming · Pydantic v2 validation

**Frontend Engineering**
Next.js 15 App Router · React 19 · TanStack Query v5 + Zustand · Authenticated live streaming with `fetch` · Forms generated from JSON Schema · Accessible, responsive custom design system · Playwright browser tests

**DevOps & Cloud**
GitHub Actions CI with lint, type-check, tests and an eval gate · Alembic migrations (verified on SQLite) · Keyless local stack · AWS CDK stacks and Dockerfiles (designed, not deployed) · Sentry

**Product Thinking**
Full PRD · Competitive analysis · GTM strategy · User research · Business model canvas — demonstrating product judgment alongside engineering skill

> Portfolio documentation: [`docs/portfolio/`](docs/portfolio/) | [`docs/`](docs/)

---

## For Investors

> The figures below are planning estimates from the business docs, not measurements. No live run with a real model has been recorded yet.

**Market** — product management and launch tooling; sizing and growth figures are in the business docs and have not been independently verified. The gap LaunchIQ targets: no tool connects research → strategy → content in one reviewed pipeline.

**Moat (planned)** — eval baselines and, later, brand-voice memory from past launches. Neither a live baseline nor brand-voice learning exists yet.

**Unit economics (estimate)** — a cheaper model for analytics, a mid-tier model for research and content, and the top tier only for strategy. A cost-per-launch estimate of ~$0.40 and a target price of $49–199/month are assumptions to validate; the app already records tokens and estimated cost per launch to measure it.

**Architecture** — designed to deploy one function per agent on AWS so that compute scales with usage; today everything runs in one API and worker process.

> Full business model: [Business Model Canvas](docs/01_Product_Thinking/06_Business_Model_Canvas.md)

---

<div align="center">

---

**Built with the Anthropic Claude SDK · Designed for AWS · 2026**

<br/>

If LaunchIQ solves a problem you care about —<br/>as a customer, investor, co-founder, or hiring manager:

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/venkataanilkumar)
[![Email](https://img.shields.io/badge/Email-Get%20In%20Touch-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:vanilkumarch@gmail.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-View%20Case%20Study-6366f1?style=for-the-badge)](docs/portfolio/03_Case_Study.md)

<br/>

<sub>Made with care by **Venkata Anil Kumar** · © 2026 LaunchIQ · MIT License</sub>

</div>
