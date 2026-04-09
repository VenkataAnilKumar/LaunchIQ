# Technical Architecture Overview
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. Architecture Philosophy

LaunchIQ is built on a **2026-native agentic AI architecture** — a multi-agent system where autonomous AI agents collaborate, use tools, maintain memory, and operate within human-in-the-loop guardrails. The system is designed to be modular, observable, and scalable from solo founder to enterprise team.

Core principles:
- **Agent-first:** Business logic lives in agents, not in monolithic services
- **Tool-augmented:** Agents use external tools (search, APIs, databases) via MCP
- **Memory-layered:** Short-term, long-term, and shared team memory
- **Observable:** Every agent action is traced, logged, and auditable
- **HITL-native:** Human approval is a first-class workflow step, not an afterthought

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              Next.js 15 + React 19 + Tailwind CSS               │
│         (Launch Input → Brief → Strategy → Content → Tracker)  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST / WebSocket / SSE
┌─────────────────────────▼───────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│                   FastAPI (Python 3.12)                         │
│              Auth (Clerk) │ Rate Limiting │ Routing             │
└──────┬──────────────────┬───────────────────────┬──────────────┘
       │                  │                       │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────────▼──────────────┐
│ ORCHESTRATOR│  │  MEMORY LAYER   │  │    TOOL REGISTRY (MCP)  │
│   AGENT     │  │                 │  │                         │
│ Claude      │  │ Short-term:     │  │ - Web Search Tool       │
│ Opus 4.6    │  │ Redis (session) │  │ - Competitor Scraper    │
│             │  │                 │  │ - HubSpot MCP Server    │
│ Coordinates │  │ Long-term:      │  │ - Slack MCP Server      │
│ all agents  │  │ Qdrant (vector) │  │ - GA4 MCP Server        │
│ via A2A     │  │                 │  │ - Email Platform MCP    │
│ protocol    │  │ Shared:         │  │                         │
└──────┬──────┘  │ PostgreSQL      │  └─────────────────────────┘
       │         └─────────────────┘
       │ Dispatches sub-agents
┌──────┴─────────────────────────────────────────────────────────┐
│                     AGENT LAYER                                │
│                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ Market          │  │ Audience        │  │ Launch        │  │
│  │ Intelligence    │  │ Insight         │  │ Strategy      │  │
│  │ Agent           │  │ Agent           │  │ Agent         │  │
│  │ (Sonnet 4.6)    │  │ (Sonnet 4.6)    │  │ (Opus 4.6)    │  │
│  │                 │  │                 │  │               │  │
│  │ Competitor scan │  │ Persona builder │  │ GTM planner   │  │
│  │ Trend research  │  │ Segment mapper  │  │ Phase builder │  │
│  │ Signal detect   │  │ Message angles  │  │ Milestone gen │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Content         │  │ Analytics &     │                      │
│  │ Generation      │  │ Feedback        │                      │
│  │ Agent           │  │ Agent           │                      │
│  │ (Sonnet 4.6)    │  │ (Haiku 4.5)     │                      │
│  │                 │  │                 │                      │
│  │ Email copy      │  │ Perf tracking   │                      │
│  │ Social posts    │  │ Optimization    │                      │
│  │ Ad headlines    │  │ Feedback loop   │                      │
│  └─────────────────┘  └─────────────────┘                      │
└────────────────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    DATA & INFRASTRUCTURE                        │
│  PostgreSQL (Supabase) │ Qdrant (vectors) │ Redis (cache/queue) │
│  AWS S3 (assets) │ Vercel (frontend) │ AWS Lambda (agents)     │
└─────────────────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    OBSERVABILITY LAYER                          │
│         LangSmith (agent traces) │ Langfuse (evals)            │
│         Sentry (errors) │ PostHog (product analytics)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Frontend Architecture

- **Framework:** Next.js 15 (App Router) + React 19
- **Styling:** Tailwind CSS + shadcn/ui components
- **State Management:** Zustand + React Query
- **Real-time:** Server-Sent Events (SSE) for agent streaming output
- **Auth:** Clerk (OAuth + magic link)
- **Hosting:** Vercel (edge deployment)

---

## 4. Backend Architecture

- **Framework:** FastAPI (Python 3.12) — async, high-performance
- **Agent Orchestration:** Claude Agent SDK
- **Task Queue:** Celery + Redis (long-running agent tasks)
- **Database ORM:** SQLAlchemy + Alembic (migrations)
- **API Style:** REST for CRUD, WebSocket for agent streaming

---

## 5. AI & Agent Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestrator | Claude Opus 4.6 | Master coordinator, planning, decisions |
| Sub-agents | Claude Sonnet 4.6 | Execution, research, generation |
| Speed tasks | Claude Haiku 4.5 | Analytics, classification, fast ops |
| Tool use | MCP Servers | External integrations via protocol |
| RAG | Qdrant + text-embedding-3 | Market knowledge retrieval |
| Agent SDK | Claude Agent SDK | Agent loop, tool calling, memory |

---

## 6. Data Architecture

- **Primary DB:** PostgreSQL via Supabase (users, launches, strategies)
- **Vector Store:** Qdrant (market embeddings, competitor data, personas)
- **Cache:** Redis (session memory, rate limiting, task queues)
- **File Storage:** AWS S3 (exports, uploads, assets)
- **Search:** Web search via Tavily API (agent tool)

---

## 7. Security Architecture

- All API keys stored in environment variables / AWS Secrets Manager
- JWT-based auth via Clerk
- Row-level security (RLS) in Supabase per tenant
- Agent outputs sanitized before rendering (XSS prevention)
- Rate limiting at API gateway level
- No user data used to train models (contractual with Anthropic)
- GDPR: Data deletion API endpoint, consent tracking

---

## 8. Observability

| Layer | Tool | What is tracked |
|-------|------|----------------|
| Agent Traces | LangSmith | Every agent step, tool call, token usage |
| Evals | Langfuse | Output quality scores, regression tests |
| Errors | Sentry | Backend + frontend exceptions |
| Product Analytics | PostHog | User flows, feature usage, funnels |
| Infrastructure | AWS CloudWatch | Lambda health, latency, errors |
