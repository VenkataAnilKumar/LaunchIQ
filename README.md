<div align="center">

<img src="docs/assets/launchiq-logo.svg" alt="LaunchIQ" width="100" height="100" />

# LaunchIQ

### AI-Powered Product Launch Intelligence

*From idea to launch-ready in minutes — not months.*

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Claude](https://img.shields.io/badge/Claude-Opus%204.6-D97706?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/lambda)
[![CI](https://img.shields.io/github/actions/workflow/status/venkataanilkumar/launchiq/pr.yml?style=for-the-badge&label=CI&logo=githubactions&logoColor=white)](https://github.com/venkataanilkumar/launchiq/actions)

<br/>

[**Live Demo**](https://launchiq.io) · [**Documentation**](docs/) · [**Architecture**](docs/03_AI_Architecture/04_Agentic_AI_Architecture.md) · [**Portfolio**](portfolio/03_Case_Study.md)

<br/>

<!--
  DEMO GIF — Record with LICEcap/Kap:
  1. make demo
  2. Fill intake form → watch 4 agents run live → HITL approve → view content
  3. Save as docs/assets/demo.gif (30-45s, 85% width)
-->

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   $ make demo                                                       │
│                                                                     │
│   ✓ PostgreSQL  ✓ Redis  ✓ Qdrant  ✓ API :8000  ✓ Frontend :3000  │
│                                                                     │
│   ⠿ Orchestrator        Planning pipeline...                        │
│   ⠿ Market Intelligence  Searching market data + competitors...     │
│   ✓ Market Intelligence  Complete  (847 tokens · 23s)              │
│                                                                     │
│     ⚡ HITL · brief_review                                          │
│        Market: $4.2B · Gap: No AI-native launch platform            │
│        → approved ✓                                                 │
│                                                                     │
│   ⠿ Audience Insight    Building personas from market data...       │
│   ✓ Audience Insight    2 personas created  (312 tokens · 8s)      │
│                                                                     │
│   ⠿ Launch Strategy     Thinking... (extended reasoning)            │
│   ✓ Launch Strategy     90-day plan ready  (1,204 tokens · 41s)    │
│                                                                     │
│     ⚡ HITL · strategy_review → approved ✓                         │
│                                                                     │
│   ⠿ Content Generation  Email + Social + Ads in parallel...         │
│   ✓ Content Generation  14 pieces across 3 formats  (891 tokens)   │
│                                                                     │
│   ✓ Pipeline complete in 3m 47s                                     │
│     → http://localhost:3000/launch/abc-123/brief                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

<sub>Replace the block above with `docs/assets/demo.gif` once recorded</sub>

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

> **HITL (Human-in-the-Loop)** is a structural pipeline gate — not a UX feature. The pipeline literally blocks on a Redis key until a human decision arrives via API. Resume from anywhere: browser, mobile, Slack, CLI.

---

## Key Features

| Feature | What it means |
|---------|--------------|
| **6-Agent Pipeline** | Orchestrator + 5 specialists, each independently deployed on AWS Lambda |
| **Extended Thinking** | Opus 4.6 reasons step-by-step on strategy — not pattern matching |
| **Live SSE Streaming** | Watch agents work in real time — token by token, agent by agent |
| **Structural HITL** | Pipeline pauses at key decisions. You review. You approve. Then it continues. |
| **MCP Tool Servers** | Tavily, HubSpot, Slack, GA4 — agents use real-world data, not hallucinations |
| **Eval Gate in CI** | Every PR checks relevance score, hallucination rate, schema compliance vs baseline |
| **3-Layer Memory** | Redis (session) + Qdrant (vectors/RAG) + PostgreSQL (structured) |
| **Parallel Content** | Email + social + ads generated simultaneously — 3× faster than sequential |
| **A/B by Default** | Every content piece ships in two variants, automatically |
| **Per-Agent Scaling** | Slow content run? Doesn't block market intelligence. Each Lambda scales independently |

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
| Vector Store | Qdrant — market data, personas, brand voice |
| Cache / Pub-Sub | Redis 7 — session state, SSE events, HITL state |
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
HITL is implemented at the orchestrator level — the pipeline blocks on a Redis key until a human decision arrives via <code>POST /api/v1/hitl/{id}/decide</code>. This means the guarantee is structural. The frontend being closed, refreshed, or on a different device doesn't matter. Resume from anywhere: browser, mobile, Slack bot, CLI.
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
<summary><strong>Why 3-layer memory instead of one database?</strong></summary>
<br/>
Each layer is optimised for its job. Redis handles sub-millisecond session reads and SSE pub/sub — a relational DB would be too slow. Qdrant enables semantic similarity search across market reports and personas — Redis can't do vectors. PostgreSQL provides ACID guarantees for launch records and billing — Qdrant isn't a transactional store. One database would mean compromising on all three.
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

# 3. Start infrastructure (PostgreSQL + Redis + Qdrant)
docker-compose up -d

# 4. Run database migrations
make migrate

# 5. Seed demo data
make seed

# 6. Start everything
make dev
```

Open **http://localhost:3000** — the demo brief is pre-loaded.

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
make eval       # Run agent eval suite vs baseline
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
│   ├── agents/                     # 6 AI agents — Lambda-deployed
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
│   │   ├── long_term/              # Qdrant — market data · personas · brand voice
│   │   └── structured/             # PostgreSQL — launches · agents · users · HITL records
│   │
│   ├── evals/                      # Eval framework + per-agent suites
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
├── docker-compose.yml              # Local dev: PostgreSQL + Redis + Qdrant
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

## Eval Results (Baseline)

| Agent | Relevance | Hallucination Rate | Schema Compliance |
|-------|-----------|-------------------|-------------------|
| Market Intelligence | 0.82 | 0.03 | 1.00 |
| Audience Insight | 0.80 | 0.02 | 1.00 |
| Launch Strategy | 0.85 | 0.04 | 1.00 |
| Content Generation | 0.78 | 0.05 | 1.00 |

Every PR must meet or exceed these scores to merge. Run locally with `make eval`.

---

## Roadmap

- [x] Multi-agent pipeline (Orchestrator + 5 workers)
- [x] HITL structural checkpoint system
- [x] MCP tool servers (Tavily, HubSpot, Slack, GA4)
- [x] Real-time SSE streaming dashboard
- [x] Eval gate in CI/CD — schema, relevance, hallucination
- [x] 3-layer memory (Redis + Qdrant + PostgreSQL)
- [x] AWS Lambda per-agent deployment
- [x] Extended thinking on strategy agent
- [x] A/B content variants by default
- [ ] Slack bot — trigger and approve launches from Slack
- [ ] Brand voice learning — improve content from past launch performance
- [ ] Competitor monitoring — weekly automated market intelligence updates
- [ ] Multi-language content generation
- [ ] White-label API for marketing agencies

---

## For Hiring Managers

This project demonstrates end-to-end production proficiency across:

**AI Engineering**
Multi-agent orchestration · Extended thinking (Opus 4.6) · MCP protocol · HITL design · Eval frameworks · RAG with Qdrant · Cognitive loop patterns (ReAct · Plan-and-Execute · Evaluator-Optimizer) · Prompt engineering with schema enforcement · Hallucination detection

**Backend Engineering**
FastAPI async architecture · SQLAlchemy 2.x async · Celery distributed tasks · Redis pub/sub · JWT auth middleware · Rate limiting · PII scrubbing pipeline · SSE streaming · Pydantic v2 validation

**Frontend Engineering**
Next.js 15 App Router · React 19 Server Components · Partial Prerendering · Zustand v5 + TanStack Query v5 · Tailwind CSS v4 · Real-time SSE integration · React Hook Form + Zod · openapi-typescript end-to-end types

**DevOps & Cloud**
AWS CDK v2 IaC · Lambda per-service architecture · ECS Fargate · Multi-stage Dockerfiles · GitHub Actions CI/CD with eval gates · Alembic migrations · Observability stack (LangSmith + Langfuse + Sentry + PostHog)

**Product Thinking**
Full PRD · Competitive analysis · GTM strategy · User research · Business model canvas — demonstrating product judgment alongside engineering skill

> Portfolio documentation: [`portfolio/`](portfolio/) | [`docs/`](docs/)

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
[![Portfolio](https://img.shields.io/badge/Portfolio-View%20Case%20Study-6366f1?style=for-the-badge)](portfolio/03_Case_Study.md)

<br/>

<sub>Made with care by **Venkata Anil Kumar** · © 2026 LaunchIQ · MIT License</sub>

</div>
