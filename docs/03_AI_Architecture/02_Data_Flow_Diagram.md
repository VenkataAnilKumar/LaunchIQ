# Data Flow Diagram
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                   │
│                         (Next.js 15 Frontend)                               │
│                                                                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────────────────┐  │
│  │  Intake     │    │  Agent Output    │    │   Launch Dashboard         │  │
│  │  Form       │    │  Stream (SSE)    │    │   (Strategy + Content)     │  │
│  └──────┬──────┘    └────────▲─────────┘    └───────────────────────────┘  │
└─────────┼───────────────────┼──────────────────────────────────────────────┘
          │ HTTPS POST        │ Server-Sent Events (streaming)
          ▼                   │
┌─────────────────────────────┼──────────────────────────────────────────────┐
│                        API GATEWAY (FastAPI)                                │
│                                                                             │
│  Auth check (Clerk JWT) → Rate limit → Route to agent worker                │
│                                                                             │
└───────────┬─────────────────┬──────────────────────────────────────────────┘
            │ Enqueue task    │ Return stream ID
            ▼                 │
┌───────────────────────┐     │
│   TASK QUEUE          │     │
│   (Celery + Redis)    │◄────┘
│                       │
│   launch_brief_task   │
└──────────┬────────────┘
           │ Worker picks up task
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         AGENT EXECUTION LAYER                            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │              ORCHESTRATOR AGENT (Claude Opus 4.6)                  │  │
│  │                                                                    │  │
│  │  Reads: User intake data from PostgreSQL                          │  │
│  │  Writes: Workflow state to Redis                                  │  │
│  │  Dispatches: Sub-agents via A2A protocol                          │  │
│  └──────────────────────────────┬─────────────────────────────────────┘  │
│                                 │                                         │
│    ┌────────────────────────────┼─────────────────────────────────┐       │
│    │                            │                                 │       │
│    ▼                            ▼                                 ▼       │
│  ┌──────────────┐   ┌──────────────────┐   ┌──────────────────────────┐  │
│  │  Market      │   │  Audience        │   │  Launch Strategy         │  │
│  │  Intelligence│   │  Insight Agent   │   │  Agent                   │  │
│  │  Agent       │   │  (Sonnet 4.6)    │   │  (Opus 4.6)              │  │
│  │  (Sonnet 4.6)│   │                  │   │                          │  │
│  │              │   │  IN: Brief       │   │  IN: Brief + Personas    │  │
│  │  IN: Product │   │  OUT: Personas   │   │  OUT: Strategy           │  │
│  │  OUT: Brief  │   │                  │   │                          │  │
│  └──────┬───────┘   └────────┬─────────┘   └──────────┬───────────────┘  │
│         │                    │                        │                   │
│         ▼                    ▼                        ▼                   │
│  ┌──────────────┐   ┌──────────────────┐   ┌──────────────────────────┐  │
│  │  Content     │   │  Analytics &     │   │  HITL Gateway            │  │
│  │  Generation  │   │  Feedback Agent  │   │  (WebSocket to browser)  │  │
│  │  Agent       │   │  (Haiku 4.5)     │   │                          │  │
│  │  (Sonnet 4.6)│   │                  │   │  Pauses workflow         │  │
│  │              │   │  IN: Metrics     │   │  Waits for user action   │  │
│  │  IN: All ctx │   │  OUT: Recs       │   │  Resumes on approval     │  │
│  │  OUT: Copy   │   │                  │   │                          │  │
│  └──────────────┘   └──────────────────┘   └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
           │                    │                        │
           ▼                    ▼                        ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           TOOL REGISTRY (MCP)                            │
│                                                                          │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  Tavily       │  │  HubSpot      │  │  Slack       │  │  GA4      │  │
│  │  Search MCP   │  │  MCP Server   │  │  MCP Server  │  │  MCP      │  │
│  │               │  │               │  │              │  │  Server   │  │
│  │  → Web search │  │  → Contacts   │  │  → Alerts    │  │  → Events │  │
│  │  → News       │  │  → Sequences  │  │  → Approvals │  │  → Goals  │  │
│  └───────────────┘  └───────────────┘  └──────────────┘  └───────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
           │                    │
           ▼                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE LAYER                          │
│                                                                          │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  PostgreSQL         │  │  Qdrant          │  │  Redis               │  │
│  │  (Supabase)         │  │  (Vector Store)  │  │  (Cache + Queue)     │  │
│  │                     │  │                  │  │                      │  │
│  │  - Users            │  │  - Market data   │  │  - Session state     │  │
│  │  - Launches         │  │    embeddings    │  │  - Agent scratchpad  │  │
│  │  - Strategies       │  │  - Competitor    │  │  - Task queue        │  │
│  │  - Personas         │  │    vectors       │  │  - Rate limit data   │  │
│  │  - Content          │  │  - Persona       │  │                      │  │
│  │  - Analytics        │  │    embeddings    │  │                      │  │
│  └─────────────────────┘  └─────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY LAYER                               │
│                                                                          │
│  LangSmith (agent traces) │ Langfuse (evals) │ Sentry (errors)          │
│  PostHog (product analytics) │ CloudWatch (infrastructure)              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Classification

| Data Type | Classification | Storage | Retention |
|-----------|---------------|---------|-----------|
| User account data | PII | PostgreSQL (encrypted) | Until deletion request |
| Product descriptions | User content | PostgreSQL | Until deletion request |
| Market research results | Derived data | Qdrant + PostgreSQL | 90 days (refreshed) |
| Generated strategies | User content | PostgreSQL | Until deletion request |
| Generated copy | User content | PostgreSQL | Until deletion request |
| Session state | Transient | Redis (TTL: 24h) | 24 hours auto-expire |
| Agent traces | Operational | LangSmith | 30 days |
| Analytics events | Behavioral | PostHog | 1 year |
| API keys (third-party) | Secret | AWS Secrets Manager | Until rotated |

---

## 3. Data Flow — User Registration

```
User → Clerk OAuth → JWT issued → FastAPI validates JWT
    → User record created in PostgreSQL (Supabase)
    → Session token stored in Redis (TTL: 24h)
    → PostHog identify() called (anonymized user ID)
```

---

## 4. Data Flow — Launch Brief Generation

```
1. User submits intake form (product name, description, target market)
2. Frontend → POST /api/launches (with JWT)
3. FastAPI validates auth → creates launch record in PostgreSQL
4. Task enqueued in Celery/Redis queue
5. Orchestrator Agent reads launch record from PostgreSQL
6. Orchestrator dispatches Market Intelligence Agent
7. Market Intel Agent → calls Tavily MCP (web search)
8. Search results → processed by Claude Sonnet 4.6
9. Structured brief → stored in PostgreSQL + embedded in Qdrant
10. HITL: Brief streamed to frontend via SSE → user approves
11. Orchestrator dispatches Audience Insight Agent (reads brief from PG)
12. Personas generated → stored in PostgreSQL
13. HITL: Personas streamed to frontend → user approves
14. [Pattern repeats for Strategy + Content agents]
15. Final launch record updated in PostgreSQL with all outputs
16. LangSmith trace completed and stored
```

---

## 5. Data Flow — Analytics & Feedback

```
1. User connects GA4 (OAuth) → tokens stored encrypted in PostgreSQL
2. Analytics Agent scheduled (daily/weekly via Celery beat)
3. Agent reads GA4 via Google Analytics MCP Server
4. Metrics aggregated → compared against launch KPIs in PostgreSQL
5. Anomalies detected → recommendations generated by Haiku 4.5
6. Recommendations stored in PostgreSQL
7. User notified via in-app notification + optional Slack alert
8. User accepts/dismisses → feedback stored for agent learning
```

---

## 6. External Data Sources

| Source | Data Type | Update Frequency | Used By |
|--------|-----------|-----------------|---------|
| Tavily Search API | Web pages, news | Real-time (per request) | Market Intelligence Agent |
| Google Analytics (GA4) | User events, conversions | Daily pull | Analytics Agent |
| HubSpot | Contacts, deals, sequences | On-demand + webhook | Content, Analytics Agents |
| Slack | Channel messages, approvals | Webhook (real-time) | Orchestrator, HITL |
