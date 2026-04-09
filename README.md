<div align="center">

# LaunchIQ

### AI-Powered Product Launch Intelligence Platform

**Your AI launch team. First strategy in 10 minutes.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![Claude](https://img.shields.io/badge/Claude-Opus%204.6-orange?style=flat-square)](https://anthropic.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Demo](#demo) · [Architecture](#architecture) · [Getting Started](#getting-started) · [Documentation](#documentation) · [Roadmap](#roadmap)

</div>

---

## The Problem

Marketing teams and founders spend **2–3 weeks** manually researching competitors, defining audiences, and writing launch strategies — before a single campaign asset is created. Tools exist for pieces of this problem, but nothing connects them with AI intelligence into a single, coherent launch workflow.

## The Solution

LaunchIQ is a **2026-native multi-agent AI platform** that autonomously researches your market, generates your go-to-market strategy, creates launch content, and tracks execution — delivering a complete, actionable launch playbook in under 10 minutes.

```
Product Description  ──►  6 AI Agents  ──►  Complete Launch Playbook
```

---

## Demo

> **Live Demo:** [launchiq.demo.url](#)
> **Demo Video:** [Watch 2-min walkthrough](#)

| Step | What Happens |
|------|-------------|
| 1 | Describe your product in plain English |
| 2 | Market Intelligence Agent scans competitors and trends in real time |
| 3 | Audience Insight Agent generates 3 buyer personas with messaging angles |
| 4 | Launch Strategy Agent creates a phased GTM plan with milestones |
| 5 | Content Agent writes email sequences, social posts, and ad copy |
| 6 | Review, approve, and execute — all in one dashboard |

---

## Architecture

LaunchIQ is a **true multi-agent system** — not a chatbot wrapper, not a prompt chain. Six specialized AI agents collaborate, share memory, use external tools via MCP, and operate within structured human-in-the-loop workflows.

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│            Next.js 15 · React 19 · Tailwind CSS             │
│         Real-time agent output streaming via SSE            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   API GATEWAY (FastAPI)                     │
│         Auth (Clerk) · Rate Limiting · Task Queue           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│             ORCHESTRATOR AGENT  (Claude Opus 4.6)           │
│     Coordinates all sub-agents · Manages workflow state     │
│          A2A protocol · Human-in-the-Loop gateway           │
└──┬──────────┬───────────┬──────────────┬────────────────────┘
   │          │           │              │
   ▼          ▼           ▼              ▼
┌──────┐  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│Market│  │Audie-│  │ Launch  │  │ Content  │  │Analytics │
│Intel │  │ nce  │  │Strategy │  │   Gen    │  │Feedback  │
│Agent │  │Agent │  │  Agent  │  │  Agent   │  │  Agent   │
│      │  │      │  │         │  │          │  │          │
│Sonnet│  │Sonnet│  │Opus 4.6 │  │Sonnet4.6 │  │Haiku 4.5 │
└──┬───┘  └──┬───┘  └────┬────┘  └────┬─────┘  └────┬─────┘
   │         │           │            │              │
   └─────────┴───────────┴────────────┴──────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                  TOOL REGISTRY (MCP)                        │
│   Tavily Search · HubSpot · Slack · GA4 · Email Platform    │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    MEMORY LAYER                             │
│  Redis (session) · Qdrant (vectors) · PostgreSQL (structured)│
└─────────────────────────────────────────────────────────────┘
```

### Agents

| Agent | Model | Role | Output |
|-------|-------|------|--------|
| Orchestrator | Claude Opus 4.6 | Coordinates all agents, manages state | Workflow plan + synthesis |
| Market Intelligence | Claude Sonnet 4.6 | Real-time competitor & trend research | Competitive brief + signals |
| Audience Insight | Claude Sonnet 4.6 | Buyer persona development | 3 personas + messaging angles |
| Launch Strategy | Claude Opus 4.6 | GTM plan creation | Phased strategy + milestones |
| Content Generation | Claude Sonnet 4.6 | Launch copywriting | Email, social, ad copy |
| Analytics & Feedback | Claude Haiku 4.5 | Performance monitoring | Optimization recommendations |

### Human-in-the-Loop (HITL)

HITL is a **first-class workflow component** — not a post-processing step. The agent pipeline structurally pauses at every major output, streams results to the UI via SSE, and waits for user approval before proceeding. Users remain in control of every strategic decision while agents do the heavy lifting.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Claude Opus 4.6 · Sonnet 4.6 · Haiku 4.5 (Anthropic) |
| **Agent Framework** | Claude Agent SDK · A2A Protocol |
| **Tool Protocol** | MCP (Model Context Protocol) |
| **Backend** | FastAPI · Python 3.12 · Celery · Redis |
| **Frontend** | Next.js 15 · React 19 · Tailwind CSS · shadcn/ui |
| **Database** | PostgreSQL (Supabase) · Qdrant (vectors) · Redis (cache) |
| **Auth** | Clerk |
| **Observability** | LangSmith · Langfuse · Sentry · PostHog |
| **Infrastructure** | Vercel · AWS Lambda · GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Docker
- Anthropic API key — [get one here](https://console.anthropic.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VenkataAnilKumar/LaunchIQ.git
cd LaunchIQ

# 2. Install Python dependencies
poetry install

# 3. Configure environment
cp .env.example .env            # Add your API keys

# 4. Start local services
docker-compose up -d            # PostgreSQL + Redis + Qdrant

# 5. Run API
poetry run uvicorn src.apps.api.main:app --reload   # API on http://localhost:8000

# 6. Run worker (separate terminal)
poetry run celery -A src.apps.api.workers.celery_app.celery_app worker --loglevel=info
```

### Environment Variables

```env
# Core
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/launchiq
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
CLERK_SECRET_KEY=sk_...
CLERK_JWT_AUDIENCE=

# Agent Tools
TAVILY_API_KEY=tvly-...

# Observability
LANGSMITH_API_KEY=ls_...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
SENTRY_DSN=https://...

# Phase 2 Integrations (optional)
HUBSPOT_API_KEY=
SLACK_BOT_TOKEN=
GA4_PROPERTY_ID=
```

---

## Project Structure

```
LaunchIQ/
├── src/
│   ├── agents/
│   │   ├── orchestrator/             # Master coordinator agent
│   │   ├── market_intelligence/      # Competitor + trend research
│   │   ├── audience_insight/         # Persona builder
│   │   ├── launch_strategy/          # GTM strategy generator
│   │   ├── content_generation/       # Launch copywriter
│   │   └── analytics_feedback/       # Performance optimizer
│   ├── apps/
│   │   ├── api/                      # FastAPI app, middleware, routers, workers
│   │   └── web/                      # Next.js app scaffold
│   ├── memory/
│   │   ├── short_term/
│   │   ├── long_term/
│   │   └── structured/
│   └── tools/
│       ├── tavily_search/
│       ├── hubspot/
│       ├── slack/
│       ├── ga4/
│       └── internal/
├── docs/
│   ├── 01_Product_Thinking/
│   ├── 02_Technical_Feasibility/
│   └── 03_AI_Architecture/
├── docker-compose.yml
├── pyproject.toml
├── turbo.json
├── pnpm-workspace.yaml
├── .github/workflows/
│   ├── pr.yml
│   └── deploy-production.yml
└── README.md
```

---

## Documentation

Core product documents are organized in [`/docs`](./docs):

| Folder | Documents | What's Inside |
|--------|-----------|--------------|
| [`01_Product_Thinking`](./docs/01_Product_Thinking) | Product and GTM docs | PRD, user research, competitive analysis, roadmap, onboarding |
| [`02_Technical_Feasibility`](./docs/02_Technical_Feasibility) | Engineering docs | architecture, implementation plan, stack decisions, security/compliance |
| [`03_AI_Architecture`](./docs/03_AI_Architecture) | Agent system docs | agent capability matrix, architecture references, data flow |

---

## Roadmap

**Phase 1 — Core Intelligence Engine** *(Completed)*
- [x] Orchestrator agent + A2A coordination
- [x] Market Intelligence Agent (competitor research + trends)
- [x] Audience Insight Agent (persona builder)
- [x] Launch Strategy Agent (GTM plan generator)
- [x] HITL checkpoint system
- [x] Real-time agent streaming UI (SSE)

**Phase 2 — Content & Execution Layer** *(Completed)*
- [x] Content Generation Agent (email, social, ad copy)
- [x] User authentication middleware + launch APIs
- [x] Async orchestration workers
- [x] Analytics feedback agent baseline
- [x] API status/event handling hardening

**Phase 3 — Intelligence & Integrations** *(Completed)*
- [x] MCP base server and tool registry
- [x] HubSpot integration (MCP)
- [x] Slack integration (MCP)
- [x] GA4 integration (MCP)
- [x] Tavily and internal tool executors

**Phase 4 — Product Experience (Current)**
- [ ] Launch Execution Tracker UI
- [ ] End-to-end web flow for brief -> personas -> strategy -> content
- [ ] Frontend production polish and state persistence
- [ ] PDF / Notion export

**Phase 5 — Reliability and Scale** *(Next)*
- [ ] Long-term vector memory optimization (cross-session learning)
- [ ] Team collaboration
- [ ] Custom brand voice learning
- [ ] Evaluation/regression automation pipeline
- [ ] Enterprise readiness (SSO, audit trails, policy controls)

---

## Key Design Decisions

**Why multi-agent over a single large prompt?**
Each domain — market research, persona building, strategy — requires different reasoning depth, different tools, and different output schemas. Separate agents allow parallel evaluation, independent iteration, and cleaner observability.

**Why Claude Agent SDK over LangGraph?**
Native integration with the LLM provider means tighter A2A protocol support, less abstraction overhead for MVP, and cleaner MCP tool wiring. LangGraph adds flexibility that isn't needed at this stage.

**Why HITL as a structural workflow step?**
Trust is built incrementally. Making human approval a pipeline-level pause (not a UX layer) means the system architecturally cannot skip human decisions — which is the right default for an AI making strategic business decisions.

> Full rationale for stack decisions: [`docs/02_Technical_Feasibility/04_Tech_Stack_Decisions.md`](./docs/02_Technical_Feasibility/04_Tech_Stack_Decisions.md)

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'feat: add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

Please open an issue first for major changes.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Venkata Anil Kumar](https://linkedin.com/in/username) — AI Engineer**

*Open to full-time AI engineering roles and founding team positions.*

[LinkedIn](#) · [Portfolio](#) · [Email](#) · [Demo](#)

</div>
