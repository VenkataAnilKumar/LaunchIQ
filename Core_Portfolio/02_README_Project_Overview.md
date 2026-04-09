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
- Structured: PostgreSQL/Supabase (launches, strategies, content)

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
Frontend     │ Next.js 15 · React 19 · Tailwind CSS · shadcn/ui · Clerk
Backend      │ FastAPI (Python 3.12) · Celery · Redis
AI / Agents  │ Claude Opus 4.6 · Sonnet 4.6 · Haiku 4.5 · Claude Agent SDK
Tool Layer   │ MCP Servers (Tavily, HubSpot, Slack, GA4)
Data         │ PostgreSQL (Supabase) · Qdrant (vectors) · Redis (cache)
Observability│ LangSmith · Langfuse · Sentry · PostHog
Infra        │ Vercel (frontend) · AWS Lambda (agent workers) · GitHub Actions (CI/CD)
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
git clone https://github.com/username/launchiq.git
cd launchiq

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your API keys

# 3. Frontend
cd ../frontend
npm install
cp .env.example .env.local    # fill in your keys

# 4. Local services
docker-compose up -d          # PostgreSQL + Redis + Qdrant

# 5. Run
uvicorn main:app --reload     # backend on :8000
npm run dev                   # frontend on :3000
```

### Environment Variables

```env
# Required
ANTHROPIC_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=

# Agent tools
TAVILY_API_KEY=

# Observability
LANGSMITH_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
SENTRY_DSN=

# Optional (Phase 2 integrations)
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
│   │   ├── orchestrator.py          # Orchestrator agent
│   │   ├── market_intelligence.py   # Market research agent
│   │   ├── audience_insight.py      # Persona builder agent
│   │   ├── launch_strategy.py       # GTM strategy agent
│   │   ├── content_generation.py    # Copywriting agent
│   │   └── analytics_feedback.py    # Analytics agent
│   ├── api/
│   │   ├── launches.py              # Launch CRUD endpoints
│   │   ├── agents.py                # Agent run endpoints
│   │   └── auth.py                  # Auth middleware
│   ├── memory/
│   │   ├── redis_store.py           # Short-term session memory
│   │   ├── qdrant_store.py          # Long-term vector memory
│   │   └── pg_store.py              # Structured persistence
│   ├── tools/
│   │   ├── tavily_mcp.py            # Web search tool
│   │   ├── hubspot_mcp.py           # HubSpot tool
│   │   └── slack_mcp.py             # Slack tool
│   └── main.py
├── frontend/
│   ├── app/
│   │   ├── (auth)/                  # Login / signup pages
│   │   ├── dashboard/               # Main launch dashboard
│   │   ├── launch/[id]/             # Individual launch view
│   │   └── onboarding/              # Intake form + agent pipeline
│   └── components/
│       ├── agents/                  # Agent activity UI
│       ├── hitl/                    # HITL checkpoint components
│       └── dashboard/               # Dashboard widgets
├── docs/                            # Full product documentation (16 docs)
├── docker-compose.yml
├── .github/workflows/               # CI/CD pipelines
└── README.md
```

---

## Roadmap

**Phase 1 (Current) — Core Intelligence**
- [x] Orchestrator + 3 core agents (Market, Audience, Strategy)
- [ ] Content Generation Agent
- [ ] Launch Execution Tracker

**Phase 2 — Integrations**
- [ ] HubSpot integration
- [ ] Slack integration
- [ ] PDF / Notion export

**Phase 3 — Intelligence & Scale**
- [ ] GA4 integration + Analytics Agent
- [ ] Long-term memory (cross-session learning)
- [ ] Team collaboration

---

## Documentation

Full product documentation available in `/docs/`:

| Document | Description |
|----------|-------------|
| `05_PRD.md` | Product Requirements Document |
| `09_Technical_Architecture.md` | System architecture + diagrams |
| `15_Product_Document.md` | Full product doc with Agentic AI Architecture 2026 |
| `16_Agent_Capability_Matrix.md` | Agent-by-agent capabilities |
| `17_Data_Flow_Diagram.md` | Data flow across all system layers |
| `18_Security_Compliance.md` | Security design + GDPR/CCPA posture |

---

## Contributing

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'feat: add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

**Venkata Anil Kumar** — AI Engineer
Building LaunchIQ as a demonstration of modern agentic AI product development.

[GitHub](#) · [LinkedIn](#) · [Demo](#)
