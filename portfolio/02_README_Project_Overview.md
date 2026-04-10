# LaunchIQ

> **Your AI launch team. First strategy in 10 minutes.**

LaunchIQ is a 2026-native, multi-agent AI platform that autonomously researches markets, generates launch strategies, creates campaign content, and tracks execution — so founders and marketers can launch faster, smarter, and with more confidence.

---

## Why LaunchIQ Exists

| The Old Way | The LaunchIQ Way |
|-------------|-----------------|
| 2–3 weeks of manual competitor research | Market Intelligence Agent completes it in 90 seconds |
| Audience personas built from gut feel | Audience Insight Agent generates 3 research-backed personas |
| Launch strategy in a disconnected slide deck | Phased GTM plan linked directly to execution tracker |
| Generic AI copy with no market context | Content Agent writes copy loaded with strategy + persona context |
| No learning loop post-launch | Analytics Agent tracks performance and recommends optimizations |

---

## Architecture Overview

LaunchIQ is a **true multi-agent system** — not a chatbot wrapper.

```
User Input (Product Description)
         │
         ▼
  Orchestrator Agent (Claude Opus 4.6)
  ├── coordinates 5 sub-agents via A2A protocol
  ├── manages workflow state in Redis
  └── synthesizes final launch playbook
         │
         ├──► Market Intelligence Agent  → Competitive brief + trends
         ├──► Audience Insight Agent     → 3 buyer personas + messaging
         ├──► Launch Strategy Agent      → Phased GTM plan + milestones
         ├──► Content Generation Agent   → Email, social, ad copy
         └──► Analytics & Feedback Agent → Performance + optimization
                   │
         Human-in-the-Loop checkpoints at every stage
                   │
         Tool Registry (MCP Servers)
         ├── Tavily Search (web research)
         ├── HubSpot MCP (CRM integration)
         ├── Slack MCP (team alerts)
         └── GA4 MCP (analytics)
```

**Memory architecture:**
- Short-term: Redis (session state, agent scratchpads)
- Long-term: Qdrant (market embeddings, competitor vectors)
- Structured: PostgreSQL (launches, strategies, content — managed via Alembic)

---

## Features

- **Launch Intelligence Brief** — AI-researched competitive landscape and trend signals
- **Buyer Persona Builder** — 3 research-backed personas with messaging angles
- **GTM Strategy Generator** — Phased launch plan with milestones and KPIs
- **Campaign Content Generator** — Email sequences, social copy, ad headlines per persona
- **Launch Execution Tracker** — Step-by-step checklist tied to your strategy
- **Performance Analytics** — Real-time metrics with AI optimization recommendations
- **Human-in-the-Loop** — Review and approve at every major agent output

---

## Tech Stack

```
Frontend     │ Next.js 15 · React 19 · Tailwind CSS v4 · shadcn/ui · Clerk
Backend      │ FastAPI (Python 3.12) · Celery · Redis
AI / Agents  │ Claude Opus 4.6 · Sonnet 4.6 · Haiku 4.5 · Claude Agent SDK
Tool Layer   │ MCP Servers (Tavily, HubSpot, Slack, GA4)
Data         │ PostgreSQL · Qdrant (vectors) · Redis (cache)
Observability│ LangSmith · Langfuse · Sentry
Infra        │ Vercel (frontend) · AWS Lambda (agent workers) · AWS ECS (API) · GitHub Actions (CI/CD)
```

---

## Getting Started

### Prerequisites

```bash
python 3.12+
node 20+
docker
anthropic api key
```

### Quick Start

```bash
# 1. Clone
git clone https://github.com/venkataanilkumar/launchiq.git
cd launchiq

# 2. Backend
cd src/apps/api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your API keys

# 3. Run DB migrations
alembic upgrade head

# 4. Frontend
cd ../../apps/web
pnpm install
cp .env.example .env.local    # fill in your keys

# 5. Local services
docker-compose up -d          # PostgreSQL + Redis + Qdrant

# 6. Run
uvicorn main:app --reload     # backend on :8000
pnpm dev                      # frontend on :3000
```

### Environment Variables

```env
# Required
ANTHROPIC_API_KEY=
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/launchiq
REDIS_URL=redis://localhost:6379/0
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=

# Agent tools
TAVILY_API_KEY=
OPENAI_API_KEY=          # embeddings (text-embedding-3-small)

# Observability
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
SENTRY_DSN=

# Optional integrations
HUBSPOT_API_KEY=
SLACK_BOT_TOKEN=
GA4_PROPERTY_ID=
```

---

## Project Structure

```
launchiq/
├── src/
│   ├── agents/
│   │   ├── _base/               # BaseAgent, CognitiveLoop, ContextBuilder, OutputValidator
│   │   ├── orchestrator/        # Orchestrator agent (Opus 4.6)
│   │   ├── market_intelligence/ # Competitive research agent
│   │   ├── audience_insight/    # Persona builder agent
│   │   ├── launch_strategy/     # GTM strategy agent
│   │   ├── content_generation/  # Copywriting agent
│   │   └── analytics_feedback/  # Analytics agent (Haiku 4.5)
│   ├── apps/
│   │   ├── api/                 # FastAPI backend
│   │   │   ├── routers/         # launches, agents, hitl, integrations, users
│   │   │   ├── services/        # launch_service, stream_service
│   │   │   ├── middleware/       # auth, rate_limit, security_headers
│   │   │   └── requirements.txt
│   │   └── web/                 # Next.js 15 frontend
│   │       ├── app/             # App Router pages
│   │       └── components/      # UI components
│   ├── memory/
│   │   ├── short_term/          # Redis session store, HITL state
│   │   ├── long_term/           # Qdrant: market_store, persona_store, brand_voice_store
│   │   └── structured/          # PostgreSQL + Alembic migrations
│   ├── tools/                   # MCP tool servers (Tavily, HubSpot, Slack, GA4)
│   └── evals/
│       ├── framework/           # Evaluator, scorer, Langfuse client
│       ├── metrics/             # relevance, hallucination, schema_compliance, edit_rate
│       ├── suites/              # per-agent eval suites
│       └── regression/          # run_regression.py + baseline.json
├── docs/                        # 22+ product documents
│   ├── 01_Product_Thinking/
│   ├── 02_Technical_Feasibility/
│   └── 03_AI_Architecture/
├── .github/workflows/           # CI/CD pipelines
├── portfolio/                   # Portfolio documents
└── README.md
```

---

## Roadmap

**Phase 1–10 (Complete)**
- [x] Base agent framework (BaseAgent, CognitiveLoop, HITL)
- [x] Orchestrator + 5 specialized agents
- [x] FastAPI backend with all routers and middleware
- [x] PostgreSQL schema + Alembic migrations
- [x] Redis short-term memory + HITL state
- [x] Qdrant long-term vector stores
- [x] MCP tool integrations (Tavily, HubSpot, Slack, GA4)
- [x] Next.js 15 frontend with SSE streaming
- [x] Eval framework + per-agent quality suites
- [x] AWS CDK infrastructure + GitHub Actions CI/CD

**Phase 11 — Beta & Growth**
- [ ] Deploy to production (Vercel + AWS ECS)
- [ ] Beta launch (10 users)
- [ ] Stripe payments
- [ ] PostHog product analytics

**Phase 12 — Intelligence**
- [ ] Cross-session learning (long-term memory feedback loop)
- [ ] Team collaboration (multi-user launches)
- [ ] PDF / Notion export
- [ ] Custom fine-tuned models

---

## Documentation

Full product documentation in `/docs/`:

| Document | Description |
|----------|-------------|
| `01_Product_Thinking/01_PRD.md` | Product Requirements Document |
| `01_Product_Thinking/05_GTM_Strategy.md` | Go-to-market strategy |
| `02_Technical_Feasibility/01_Technical_Architecture.md` | System architecture |
| `02_Technical_Feasibility/04_Tech_Stack_Decisions.md` | Stack decisions + rationale |
| `02_Technical_Feasibility/05_Security_Compliance.md` | Security design + GDPR posture |
| `03_AI_Architecture/01_Agent_Capability_Matrix.md` | Agent-by-agent capabilities |
| `03_AI_Architecture/02_Data_Flow_Diagram.md` | Data flow across all layers |

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

**Venkata Anil Kumar** — AI Engineer
Building LaunchIQ as a demonstration of modern agentic AI product development.

[GitHub](https://github.com/venkataanilkumar) · [LinkedIn](https://linkedin.com/in/venkataanilkumar) · [Email](mailto:vanilkumarch@gmail.com)
