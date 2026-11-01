<div align="center">

<img src="docs/assets/launchiq-logo.svg" alt="LaunchIQ" width="100" height="100" />

# LaunchIQ

### AI-Powered Product Launch Intelligence

*From idea to launch-ready in minutes — not months.*

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-D97706?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/lambda)
[![CI](https://img.shields.io/github/actions/workflow/status/venkataanilkumar/launchiq/pr.yml?style=for-the-badge&label=CI&logo=githubactions&logoColor=white)](https://github.com/venkataanilkumar/launchiq/actions)

<br/>

[**Live Demo**](https://launchiq.io) · [**Documentation**](docs/) · [**Architecture**](docs/03_AI_Architecture/04_Agentic_AI_Architecture.md) · [**Portfolio**](docs/portfolio/03_Case_Study.md)

⭐ If LaunchIQ helps your team, please star this repository to support the project.

<br/>

<img src="docs/assets/demo.svg" alt="LaunchIQ — 6 AI agents deliver a complete launch playbook in under 3 minutes" width="100%"/>

</div>

---

## The Problem

> *"We spent 6 weeks on launch prep. Hired 3 agencies. Still missed our ICP."*

Product launches fail not because of bad products — but because teams lack the intelligence to launch precisely.

- Market research takes **weeks** and costs **thousands**
- Persona development is **guesswork** without real data
- Launch strategies are **copy-pasted templates** from 2019
- Content is written by committees with **no signal from the market**

**LaunchIQ fixes this with a 6-agent AI pipeline that does in 4 minutes what agencies charge $50,000 to do in 6 weeks.**

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

</td>
</tr>
</table>

---

## The Agent Pipeline

```
  Your Product Brief
         │
         ▼
╔════════════════════════════════════════════════════════════════╗
║                    ORCHESTRATOR AGENT                          ║
║              claude-opus-4.6 · Extended Thinking               ║
║      Coordinates · Validates · Manages HITL Checkpoints        ║
╚══════╤═════════════════════════════════════════╤══════════════╝
       │                                         │
       ▼                                         ▼
┌──────────────────┐               ┌──────────────────────┐
│ MARKET           │               │ AUDIENCE INSIGHT     │
│ INTELLIGENCE     │──────────────▶│                      │
│                  │               │ Persona Builder      │
│ Tavily Search    │               │ Segment Mapper       │
│ Competitor Intel │               │ Message Hook Gen     │
│ Trend Detection  │               │ claude-sonnet-4.6    │
│ claude-sonnet    │               └──────────┬───────────┘
└──────────────────┘                          │
       ⚡ HITL: brief_review                  │
                              ┌───────────────▼───────────────┐
                              │       LAUNCH STRATEGY         │
                              │                               │
                              │  90-Day Phased Plan           │
                              │  Channel Selection            │
                              │  Budget Allocation            │
                              │  Risk Analysis                │
                              │  claude-opus-4.6 + Thinking   │
                              └───────────────┬───────────────┘
                                    ⚡ HITL: strategy_review
                    ┌───────────────────────────────────────────┐
                    │          CONTENT GENERATION               │
                    │                                           │
                    │  Email Sequence · Social Posts · Ad Copy  │
                    │  A/B Variants · Brand Voice Matched       │
                    │  asyncio.gather() — 3 streams parallel    │
                    │  claude-sonnet-4.6                        │
                    └───────────────────┬───────────────────────┘
                                        │
                    ┌───────────────────▼───────────────────────┐
                    │        ANALYTICS & FEEDBACK               │
                    │                                           │
                    │  GA4 Integration · Performance Scoring    │
                    │  Optimization Recommendations             │
                    │  claude-haiku-4.5 (cost-optimized)        │
                    └───────────────────────────────────────────┘
                                        │
                              ┌─────────▼──────────┐
                              │  Your Launch Brief  │
                              │  Ready in ~4 min    │
                              └────────────────────┘
```

> **HITL (Human-in-the-Loop)** is a structural pipeline gate — not a UX feature. At a checkpoint the orchestrator stores the pending review in the database and *stops* (no worker is held while waiting). A decision arriving via `POST /api/v1/hitl/{id}/decide` is saved, schema-validated if it carries edits, and enqueues a resume that skips every agent that already finished. Resume from anywhere: browser, mobile, Slack, CLI.

---

## Key Features

| Feature | What it means |
|---------|--------------|
| **Multi-Agent Pipeline** | Orchestrator + 4 pipeline agents (market, audience, strategy, content) + an on-demand post-launch analytics agent. Each has a Lambda-style handler; the deployed topology is not verified |
| **Extended Thinking** | Opus 4.6 reasons step-by-step on strategy — not pattern matching |
| **Live SSE Streaming** | Watch agents work in real time — token by token, agent by agent |
| **Structural HITL** | Pipeline pauses at two review checkpoints. Approve, edit (schema-validated) or reject; stale clicks get a 409 instead of approving the next review blind |
| **MCP Tool Servers** | Tavily, HubSpot, Slack, GA4 — agents use real-world data, not hallucinations |
| **Eval Gate in CI** | Every PR runs the real agents over a brief corpus (fake LLM) and gates on schema, grounding, injection and error regressions |
| **Memory** | PostgreSQL/SQLite (launches, agent runs, HITL records) + Redis (events, rate limiting) |
| **Parallel Content** | Email + social + ads generated simultaneously — 3× faster than sequential |
| **A/B by Default** | Every content piece ships in two variants, automatically |
| **Grounded & Guarded** | Trend sources must be URLs the agent actually got from search; every prompt treats briefs, web pages and human edits as data, not instructions; per-launch cost budget |

---

## Tech Stack

### AI & Agents

| Component | Technology | Role |
|-----------|-----------|------|
| Agent Framework | Anthropic Claude SDK (native) | Orchestration + tool use |
| Orchestrator | claude-opus-4.6 + Extended Thinking | Pipeline coordination + deep reasoning |
| Market + Audience + Content | claude-sonnet-4.6 | Balanced capability + cost |
| Analytics | claude-haiku-4.5 | Cost-optimized feedback loop |
| Tool Protocol | MCP (Model Context Protocol) | Standardised external tool access |
| Agent Communication | A2A Protocol | Structured inter-agent messaging |
| Reasoning Patterns | ReAct · Chain-of-Thought · Plan-and-Execute · Evaluator-Optimizer | Per-agent cognitive strategy |

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
| Framework | Next.js 15 — App Router + Partial Prerendering |
| UI Runtime | React 19 — Server Components, Compiler, `use()` hook |
| Styling | Tailwind CSS v4 + shadcn/ui + Radix UI primitives |
| Server State | TanStack Query v5 |
| Client State | Zustand v5 + Immer |
| Real-time | Server-Sent Events (native `EventSource`) |
| Forms | React Hook Form v8 + Zod |
| Type Safety | openapi-typescript — types auto-generated from FastAPI schema |

### Infrastructure & Observability

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
<summary><strong>Why one Lambda per agent instead of a monolith?</strong></summary>
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
LLM outputs are non-deterministic. Unit tests with mocked Claude responses don't catch prompt regressions. The eval gate runs real Anthropic API calls against a fixed test corpus and compares relevance score, hallucination rate, and schema compliance against a locked baseline. A PR that degrades agent quality cannot merge — regardless of whether all unit tests pass.
</details>

<details>
<summary><strong>Why MCP tool servers instead of direct API calls?</strong></summary>
<br/>
MCP (Model Context Protocol) is the 2026 standard for AI-tool integration. Each tool server is self-contained with its own auth, schema validation, and rate limiting. Agents declare which tools they need — the cognitive loop handles execution. Swapping Tavily for a different search provider changes one file. Adding a new tool to any agent takes minutes.
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

# 5. Seed demo data
make seed

# 6. Start everything
make dev
```

Open **http://localhost:3000** — the demo brief is pre-loaded.

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
make seed       # Load demo launch data
make demo       # migrate + seed + dev (full one-command demo)
```

---

## Project Structure

```
launchiq/
│
├── src/
│   ├── agents/                     # Orchestrator + 5 agents (Lambda-style handlers)
│   │   ├── _base/                  # BaseAgent · CognitiveLoop · OutputValidator
│   │   ├── orchestrator/           # Pipeline coordinator (Opus 4.6 + Thinking)
│   │   ├── market_intelligence/    # Web research + competitor analysis
│   │   ├── audience_insight/       # Persona builder + messaging framework
│   │   ├── launch_strategy/        # 90-day phased launch plan
│   │   ├── content_generation/     # Email · social · ads (parallel)
│   │   └── analytics_feedback/     # GA4 + performance recommendations
│   │
│   ├── apps/
│   │   ├── api/                    # FastAPI backend — ECS Fargate
│   │   │   ├── middleware/         # Auth · PII scrubber · rate limit · security headers
│   │   │   ├── routers/            # launches · agents · hitl · integrations · health
│   │   │   ├── services/           # launch · agent · stream · hitl
│   │   │   └── workers/            # Celery tasks
│   │   └── web/                    # Next.js 15 frontend — Vercel
│   │       ├── app/                # App Router — Server + Client components
│   │       ├── components/         # agents/ · hitl/ · launch/ · ui/
│   │       ├── store/              # Zustand stores
│   │       └── lib/                # api client · SSE hook · query client
│   │
│   ├── tools/                      # MCP tool servers
│   │   ├── tavily_search/          # Web research
│   │   ├── hubspot/                # CRM integration
│   │   ├── slack/                  # Team notifications
│   │   ├── ga4/                    # Analytics data
│   │   └── internal/               # LaunchIQ session data access
│   │
│   ├── memory/
│   │   ├── short_term/             # Redis — session state · HITL · scratchpad
│   │   └── structured/             # PostgreSQL — launches · agents · users · HITL records
│   │
│   ├── evals/                      # Eval corpus + pipeline evaluator + regression gate
│   │   ├── framework/              # Evaluator · Scorer · Langfuse client · Reporter
│   │   ├── metrics/                # relevance · hallucination · schema · edit_rate
│   │   ├── suites/                 # Per-agent test cases + expected outputs
│   │   └── regression/             # run_regression.py · baseline.json · update_baseline.py
│   │
│   └── infra/                      # AWS CDK stacks + Docker
│       ├── aws/stacks/             # agents · api · data · secrets
│       └── docker/                 # api · worker · mcp Dockerfiles
│
├── docs/
│   ├── 01_Product_Thinking/        # PRD · Research · Competitive · GTM · Business Model
│   ├── 02_Technical_Feasibility/   # Architecture · Security · Implementation Plan
│   └── 03_AI_Architecture/         # Agent Matrix · Data Flow · Agentic AI 2026
│
├── .github/workflows/              # pr · deploy-staging · deploy-production · eval-scheduled
├── docker-compose.yml              # Local dev: PostgreSQL + Redis
├── pyproject.toml                  # Python deps (Poetry)
├── turbo.json                      # Turborepo pipeline
└── Makefile                        # dev · test · eval · migrate · seed · demo
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
create launch → live agent progress → review checkpoint → read results mid-pause → approve / edit / reject → completed brief → Markdown export → post-launch analytics from supplied metrics; per-user isolation; failed-agent retry; cost budget.

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
Multi-agent orchestration · Extended thinking (Opus 4.6) · MCP protocol · HITL design · Eval frameworks · Cognitive loop patterns (ReAct · Plan-and-Execute · Evaluator-Optimizer) · Prompt engineering with schema enforcement · Hallucination detection

**Backend Engineering**
FastAPI async architecture · SQLAlchemy 2.x async · Celery distributed tasks · Redis pub/sub · JWT auth middleware · Rate limiting · PII scrubbing pipeline · SSE streaming · Pydantic v2 validation

**Frontend Engineering**
Next.js 15 App Router · React 19 Server Components · Partial Prerendering · Zustand v5 + TanStack Query v5 · Tailwind CSS v4 · Real-time SSE integration · React Hook Form + Zod · openapi-typescript end-to-end types

**DevOps & Cloud**
AWS CDK v2 IaC · Lambda per-service architecture · ECS Fargate · Multi-stage Dockerfiles · GitHub Actions CI/CD with eval gates · Alembic migrations · Observability stack (LangSmith + Langfuse + Sentry + PostHog)

**Product Thinking**
Full PRD · Competitive analysis · GTM strategy · User research · Business model canvas — demonstrating product judgment alongside engineering skill

> Portfolio documentation: [`docs/portfolio/`](docs/portfolio/) | [`docs/`](docs/)

---

## For Investors

**Market** — $4.2B product management tools market, 18% YoY growth. Every product team launches products. No AI-native solution connects research → strategy → content in one pipeline at this quality level.

**Moat** — Agent eval baselines + brand voice memory create a data flywheel. The product improves with every launch. MCP tool integrations (HubSpot, Slack, GA4) create workflow lock-in.

**Unit Economics** — Claude Haiku for analytics, Sonnet for research, Opus only where deep reasoning is needed. Estimated API cost per launch: ~$0.40. Target pricing: $49–199/month.

**Architecture** — Built Lambda-first. Each agent scales to zero when idle. Compute costs scale with usage, not headcount.

> Full business model: [Business Model Canvas](docs/01_Product_Thinking/06_Business_Model_Canvas.md)

---

<div align="center">

---

**Built with the Anthropic Claude SDK · Deployed on AWS · Designed for 2026**

<br/>

If LaunchIQ solves a problem you care about —<br/>as a customer, investor, co-founder, or hiring manager:

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/venkataanilkumar)
[![Email](https://img.shields.io/badge/Email-Get%20In%20Touch-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:vanilkumarch@gmail.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-View%20Case%20Study-6366f1?style=for-the-badge)](docs/portfolio/03_Case_Study.md)

<br/>

<sub>Made with care by **Venkata Anil Kumar** · © 2026 LaunchIQ · MIT License</sub>

</div>

<!-- quickdraw-doc-touch -->
