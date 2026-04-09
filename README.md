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
- Node.js 20+
- Docker
- Anthropic API key — [get one here](https://console.anthropic.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/username/launchiq.git
cd launchiq

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your API keys

# 3. Frontend setup
cd ../frontend
npm install
cp .env.example .env.local      # Add your keys

# 4. Start local services
docker-compose up -d            # PostgreSQL + Redis + Qdrant

# 5. Run
uvicorn main:app --reload       # API on http://localhost:8000
npm run dev                     # UI  on http://localhost:3000
```

### Environment Variables

```env
# Core
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...

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
launchiq/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py           # Master coordinator agent
│   │   ├── market_intelligence.py    # Competitor & trend research
│   │   ├── audience_insight.py       # Buyer persona builder
│   │   ├── launch_strategy.py        # GTM strategy generator
│   │   ├── content_generation.py     # Launch copywriter
│   │   └── analytics_feedback.py     # Performance optimizer
│   ├── api/
│   │   ├── launches.py               # Launch CRUD endpoints
│   │   ├── agents.py                 # Agent run + stream endpoints
│   │   └── auth.py                   # JWT middleware
│   ├── memory/
│   │   ├── redis_store.py            # Session memory
│   │   ├── qdrant_store.py           # Vector memory
│   │   └── pg_store.py               # Structured persistence
│   ├── tools/
│   │   ├── tavily_mcp.py             # Web search MCP tool
│   │   ├── hubspot_mcp.py            # HubSpot MCP tool
│   │   └── slack_mcp.py              # Slack MCP tool
│   └── main.py
├── frontend/
│   ├── app/
│   │   ├── (auth)/                   # Login / signup
│   │   ├── dashboard/                # Main launch dashboard
│   │   ├── launch/[id]/              # Individual launch view
│   │   └── onboarding/               # Intake form + agent pipeline
│   └── components/
│       ├── agents/                   # Agent activity UI + streaming
│       ├── hitl/                     # HITL checkpoint components
│       └── dashboard/                # Dashboard widgets
├── docs/
│   ├── 01_Core_Portfolio/            # One-pager, case study, portfolio
│   ├── 02_Product_Thinking/          # PRD, user research, competitive analysis, roadmap
│   ├── 03_Technical_Feasibility/     # Architecture, tech stack, demo script
│   ├── 04_Business_Potential/        # GTM strategy, business model canvas
│   ├── 05_Product_Document/          # Full product doc + agentic AI architecture
│   ├── 06_Agentic_AI_Architecture/   # Agent matrix, data flow diagrams
│   ├── 07_Security_Compliance/       # Security design, GDPR posture
│   ├── 08_UX_Onboarding/             # Onboarding flow, user journey map
│   └── 09_Personal_Branding/         # Role & contribution summary
├── docker-compose.yml
├── .github/workflows/
│   ├── ci.yml                        # Test + lint on PR
│   └── deploy.yml                    # Deploy to Vercel + AWS on merge
└── README.md
```

---

## Documentation

20 product documents organized across 9 categories in [`/docs`](./docs):

| Folder | Documents | What's Inside |
|--------|-----------|--------------|
| [`01_Product_Thinking`](./docs/01_Product_Thinking) | 8 docs | PRD, user research, competitive analysis, roadmap, product document, GTM, BMC, onboarding |
| [`02_Technical_Feasibility`](./docs/02_Technical_Feasibility) | 5 docs | Architecture, tech stack decisions, demo script, GitHub README, security & compliance |
| [`03_AI_Architecture`](./docs/03_AI_Architecture) | 2 docs | Agent capability matrix, data flow diagram |

---

## Roadmap

**Phase 1 — Core Intelligence Engine** *(Weeks 1–4)*
- [x] Orchestrator agent + A2A coordination
- [x] Market Intelligence Agent (competitor research + trends)
- [x] Audience Insight Agent (persona builder)
- [x] Launch Strategy Agent (GTM plan generator)
- [x] HITL checkpoint system
- [x] Real-time agent streaming UI (SSE)

**Phase 2 — Content & Execution Layer** *(Weeks 5–8)*
- [ ] Content Generation Agent (email, social, ad copy)
- [ ] Launch Execution Tracker
- [ ] PDF / Notion export
- [ ] User authentication + multi-launch management

**Phase 3 — Intelligence & Integrations** *(Weeks 9–12)*
- [ ] Analytics & Feedback Agent
- [ ] HubSpot integration (MCP)
- [ ] Slack integration (MCP)
- [ ] GA4 integration (MCP)
- [ ] Long-term vector memory (cross-session learning)

**Phase 4 — Scale** *(Post-Beta)*
- [ ] Team collaboration
- [ ] Custom brand voice learning
- [ ] Enterprise contracts + SSO

---

## Key Design Decisions

**Why multi-agent over a single large prompt?**
Each domain — market research, persona building, strategy — requires different reasoning depth, different tools, and different output schemas. Separate agents allow parallel evaluation, independent iteration, and cleaner observability.

**Why Claude Agent SDK over LangGraph?**
Native integration with the LLM provider means tighter A2A protocol support, less abstraction overhead for MVP, and cleaner MCP tool wiring. LangGraph adds flexibility that isn't needed at this stage.

**Why HITL as a structural workflow step?**
Trust is built incrementally. Making human approval a pipeline-level pause (not a UX layer) means the system architecturally cannot skip human decisions — which is the right default for an AI making strategic business decisions.

> Full rationale for all 10 stack decisions: [`docs/03_Technical_Feasibility/12_Tech_Stack_Decisions.md`](./docs/03_Technical_Feasibility/12_Tech_Stack_Decisions.md)

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
