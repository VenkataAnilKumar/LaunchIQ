# End-to-End Product Architecture
## LaunchIQ — AI-Powered Product Launch Intelligence Platform
### 2026 Native Architecture

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. Architecture Overview

LaunchIQ is built as a **cloud-native, agent-first, edge-optimised SaaS platform**. Every architectural layer is designed for the 2026 reality: autonomous AI agents as the primary compute unit, MCP as the universal tool standard, serverless-first infrastructure, and observability as a non-negotiable foundation.

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    LAUNCHIQ — FULL PRODUCT ARCHITECTURE                 ║
║                                                                          ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │  LAYER 1 — CLIENT                                               │   ║
║  │  Browser · Mobile PWA · Embedded Widget (future)               │   ║
║  └──────────────────────────────┬───────────────────────────────────┘   ║
║                                 │ HTTPS / WSS / SSE                      ║
║  ┌──────────────────────────────▼───────────────────────────────────┐   ║
║  │  LAYER 2 — EDGE & CDN                                           │   ║
║  │  Vercel Edge Network · Edge Functions · Image CDN               │   ║
║  └──────────────────────────────┬───────────────────────────────────┘   ║
║                                 │                                        ║
║  ┌──────────────────────────────▼───────────────────────────────────┐   ║
║  │  LAYER 3 — FRONTEND APPLICATION                                 │   ║
║  │  Next.js 15 (App Router) · React 19 · Tailwind · shadcn/ui      │   ║
║  │  Zustand (state) · React Query (server state) · Clerk (auth UI) │   ║
║  └──────────────────────────────┬───────────────────────────────────┘   ║
║                                 │ REST · SSE · WebSocket                 ║
║  ┌──────────────────────────────▼───────────────────────────────────┐   ║
║  │  LAYER 4 — API GATEWAY                                          │   ║
║  │  FastAPI (Python 3.12) · AWS ECS (always-on)                   │   ║
║  │  Clerk JWT Auth · Rate Limiter · Input Sanitizer · Router       │   ║
║  └───────────┬──────────────────────────────┬────────────────────--┘   ║
║              │ sync                          │ async tasks               ║
║  ┌───────────▼──────────┐      ┌─────────────▼────────────────────────┐ ║
║  │  LAYER 5 — REALTIME  │      │  LAYER 6 — TASK QUEUE               │ ║
║  │  SSE Stream Manager  │      │  Celery Workers · Redis Broker       │ ║
║  │  WebSocket Manager   │      │  Agent task isolation per launch     │ ║
║  └───────────┬──────────┘      └─────────────┬────────────────────────┘ ║
║              │                               │                           ║
║  ┌───────────▼───────────────────────────────▼────────────────────────┐  ║
║  │  LAYER 7 — AGENT ORCHESTRATION                                    │  ║
║  │  Claude Agent SDK · A2A Protocol · Orchestrator Agent (Opus 4.6) │  ║
║  │  Workflow State Machine · HITL Gateway · Retry Engine            │  ║
║  └────────────────────────────────┬───────────────────────────────────┘  ║
║                                   │ dispatches                            ║
║  ┌────────────────────────────────▼───────────────────────────────────┐  ║
║  │  LAYER 8 — AGENT LAYER (AWS Lambda — serverless, isolated)        │  ║
║  │                                                                   │  ║
║  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐               │  ║
║  │  │ Market      │ │ Audience    │ │ Launch        │               │  ║
║  │  │ Intelligence│ │ Insight     │ │ Strategy      │               │  ║
║  │  │ Sonnet 4.6  │ │ Sonnet 4.6  │ │ Opus 4.6      │               │  ║
║  │  └─────────────┘ └─────────────┘ └───────────────┘               │  ║
║  │  ┌─────────────┐ ┌─────────────┐                                 │  ║
║  │  │ Content     │ │ Analytics & │                                 │  ║
║  │  │ Generation  │ │ Feedback    │                                 │  ║
║  │  │ Sonnet 4.6  │ │ Haiku 4.5   │                                 │  ║
║  │  └─────────────┘ └─────────────┘                                 │  ║
║  └────────────────────────────────┬───────────────────────────────────┘  ║
║              ┌─────────────────┬──┘ ──────────────┐                      ║
║              │                 │                   │                      ║
║  ┌───────────▼──────┐ ┌────────▼──────┐ ┌─────────▼──────────────────┐  ║
║  │  LAYER 9         │ │  LAYER 10     │ │  LAYER 11                  │  ║
║  │  TOOL REGISTRY   │ │  MEMORY LAYER │ │  GUARDRAILS & GOVERNANCE   │  ║
║  │  (MCP)           │ │               │ │                            │  ║
║  │                  │ │ Redis         │ │ Policy Engine              │  ║
║  │  Tavily Search   │ │ Qdrant        │ │ (Pre-tool execution)       │  ║
║  │  HubSpot MCP     │ │ PostgreSQL    │ │                            │  ║
║  │  Slack MCP       │ │ (Supabase)    │ │ Input validator            │  ║
║  │  GA4 MCP         │ │               │ │ Output validator           │  ║
║  │  Email MCP       │ │               │ │ PII scrubber               │  ║
║  └──────────────────┘ └───────────────┘ │ Citation enforcer          │  ║
║                                         └────────────────────────────┘  ║
║  ┌────────────────────────────────────────────────────────────────────┐  ║
║  │  LAYER 12 — OBSERVABILITY                                         │  ║
║  │  LangSmith · Langfuse · Sentry · PostHog · AWS CloudWatch        │  ║
║  └────────────────────────────────────────────────────────────────────┘  ║
║  ┌────────────────────────────────────────────────────────────────────┐  ║
║  │  LAYER 13 — INFRASTRUCTURE & PLATFORM                            │  ║
║  │  Vercel · AWS Lambda · AWS S3 · AWS Secrets Manager · GitHub CI  │  ║
║  └────────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 2. Layer-by-Layer Deep Dive

---

### Layer 1 — Client

| Client | Technology | Notes |
|--------|-----------|-------|
| Web browser | Next.js 15 SSR + CSR | Primary interface |
| Mobile PWA | Next.js PWA config | Responsive, offline-ready |
| Embedded widget | React iframe component | Future — embed in Notion, Slack |

**Real-time communication:**
- **SSE (Server-Sent Events):** Agent output streaming — one-directional, lightweight
- **WebSocket:** HITL bi-directional communication — pause/resume pipeline
- **REST:** CRUD operations — launches, users, settings

---

### Layer 2 — Edge & CDN

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Global CDN | Vercel Edge Network | Sub-50ms static asset delivery worldwide |
| Edge Functions | Vercel Edge Runtime | Auth middleware, geo-routing, A/B flags |
| Image CDN | Vercel Image Optimization | Auto-optimised images for all screen sizes |
| DDoS protection | Vercel built-in | Rate limiting at edge layer |

**2026 pattern:** Edge-first — all static content and auth checks resolved at the edge before hitting the origin server.

---

### Layer 3 — Frontend Application

```
app/
├── (auth)/               # Clerk-managed auth routes
│   ├── sign-in/
│   └── sign-up/
├── (app)/                # Authenticated app shell
│   ├── dashboard/        # Launch overview
│   ├── launch/
│   │   ├── new/          # Intake form
│   │   └── [id]/         # Individual launch view
│   │       ├── brief/    # Market Intelligence output
│   │       ├── personas/ # Audience Insight output
│   │       ├── strategy/ # Launch Strategy output
│   │       ├── content/  # Content Generation output
│   │       └── tracker/  # Execution tracker
│   └── settings/         # User + org settings
└── api/                  # Next.js API routes (thin proxy to FastAPI)
```

**State management:**
- **Zustand:** Agent run status, HITL state, UI preferences
- **React Query:** Server state — launches, strategies, content (cached + invalidated)
- **React 19 concurrent:** Smooth streaming output rendering without UI freeze

**Real-time agent streaming (SSE):**
```
FastAPI SSE endpoint
      ↓
Redis Pub/Sub (agent worker → SSE endpoint)
      ↓
Next.js EventSource client
      ↓
React streaming component (renders tokens as they arrive)
```

---

### Layer 4 — API Gateway

```
FastAPI Routes:

POST   /api/v1/launches              # Create new launch
GET    /api/v1/launches              # List user launches
GET    /api/v1/launches/{id}         # Get launch detail
DELETE /api/v1/launches/{id}         # Delete launch

POST   /api/v1/launches/{id}/run     # Trigger full agent pipeline
POST   /api/v1/launches/{id}/hitl    # Submit HITL decision
GET    /api/v1/launches/{id}/stream  # SSE stream for agent output

GET    /api/v1/agents/status/{run_id} # Get agent run status
POST   /api/v1/agents/retry/{run_id}  # Retry failed agent

POST   /api/v1/integrations/hubspot   # Connect HubSpot
POST   /api/v1/integrations/slack     # Connect Slack
POST   /api/v1/integrations/ga4       # Connect GA4

GET    /api/v1/health                 # Health check
GET    /api/v1/metrics                # Internal metrics (admin)
```

**Middleware stack (in order):**
1. CORS headers
2. Security headers (HSTS, CSP, X-Frame-Options)
3. Clerk JWT validation
4. Rate limiter (per user: 100 req/min, 10 agent runs/hour)
5. PII scrubber (remove emails, phones from product descriptions)
6. Request logger (structured JSON → CloudWatch)
7. Route handler

---

### Layer 5 — Realtime Layer

```
SSE Architecture:
─────────────────
Agent Worker (Lambda)
    │ publishes event
    ▼
Redis Pub/Sub channel: "launch:{id}:stream"
    │ subscribes
    ▼
FastAPI SSE endpoint (async generator)
    │ streams
    ▼
Next.js EventSource
    │ renders
    ▼
React streaming component


HITL WebSocket Architecture:
─────────────────────────────
User clicks [Approve / Edit / Regenerate]
    │
    ▼
WebSocket → FastAPI WebSocket handler
    │
    ▼
Redis: workflow state → APPROVED/REGENERATE
    │
    ▼
Celery: resumes paused agent pipeline
    │
    ▼
SSE: next agent output streams to client
```

---

### Layer 6 — Task Queue

| Component | Technology | Configuration |
|-----------|-----------|---------------|
| Task broker | Redis | Separate DB from session cache |
| Worker framework | Celery 5.x | Async, priority queues |
| Task routing | Per-agent queues | `market_intel`, `audience`, `strategy`, `content`, `analytics` |
| Retry policy | Exponential backoff | Max 3 retries, 2x backoff |
| Task timeout | Per-agent | Market: 120s, Strategy: 90s, Content: 180s |
| Dead letter queue | Redis DLQ | Failed tasks archived for debugging |

**Task isolation:** Each launch run gets its own Celery group — agents for one launch cannot interfere with another.

---

### Layer 7 — Agent Orchestration

```
Orchestration Engine:
─────────────────────
1. Receive launch run request from API Gateway
2. Load user intake from PostgreSQL
3. Write workflow plan to Redis:
   {
     launch_id: uuid,
     stages: [market_intel, audience, strategy, content, analytics],
     current_stage: "market_intel",
     status: "running",
     hitl_required: true,
     context: {compressed_context_object}
   }
4. Dispatch Market Intelligence Agent (Celery task)
5. Monitor Redis for HITL_PENDING signal
6. Stream HITL checkpoint to frontend (SSE)
7. Wait for user decision (WebSocket)
8. On approval → dispatch next agent
9. On regenerate → re-dispatch current agent with feedback
10. Repeat until all stages complete
11. Synthesize final launch playbook → PostgreSQL
12. Mark launch as COMPLETE in Redis + PostgreSQL
```

**Workflow State Machine:**
```
CREATED → RUNNING → HITL_PENDING → APPROVED → RUNNING → ... → COMPLETE
                              ↓
                         REGENERATING → RUNNING
                              ↓
                           FAILED → (notify user)
```

---

### Layer 8 — Agent Layer

Each agent is deployed as an **isolated AWS Lambda function** — serverless, scale-to-zero, independently deployable.

| Agent | Lambda Config | Cold Start Mitigation |
|-------|-------------|----------------------|
| Orchestrator | 512MB, 15min timeout | Provisioned concurrency (always warm) |
| Market Intelligence | 256MB, 5min timeout | On-demand (acceptable cold start) |
| Audience Insight | 256MB, 3min timeout | On-demand |
| Launch Strategy | 512MB, 5min timeout | Provisioned concurrency (critical path) |
| Content Generation | 256MB, 5min timeout | On-demand |
| Analytics & Feedback | 128MB, 2min timeout | On-demand (async, not time-sensitive) |

**Agent execution per Lambda invocation:**
```python
# Each Lambda runs the same pattern
def handler(event, context):
    agent = build_agent(event["agent_type"])       # Load agent identity
    context = load_context(event["launch_id"])      # Load from PostgreSQL + Qdrant
    result = agent.run(                             # Claude Agent SDK loop
        task=event["task"],
        context=context,
        tools=get_tools(event["agent_type"]),       # MCP tools scoped per agent
        memory=get_memory(event["launch_id"])       # Redis scratchpad
    )
    validate_output(result)                         # Guardrails layer
    persist_output(result, event["launch_id"])      # Write to PostgreSQL + Qdrant
    notify_orchestrator(event["launch_id"], result) # Redis pub → Celery signal
    return result
```

---

### Layer 9 — Tool Registry (MCP)

```
MCP Server Registry:
────────────────────
Each MCP server is a standalone service exposing tools via MCP protocol.

┌─────────────────────────────────────────────────────────────────┐
│  MCP Server          │ Hosted On      │ Tools Exposed           │
├─────────────────────────────────────────────────────────────────┤
│  Tavily Search MCP   │ Tavily Cloud   │ web_search, news_search  │
│  HubSpot MCP         │ HubSpot Cloud  │ contacts, deals, emails  │
│  Slack MCP           │ Slack Cloud    │ send_message, get_channel│
│  GA4 MCP             │ Google Cloud   │ get_events, get_goals    │
│  Email Platform MCP  │ Loops Cloud    │ send_sequence, get_stats │
│  Internal Tools MCP  │ AWS Lambda     │ personas, gtm_frameworks │
└─────────────────────────────────────────────────────────────────┘

Tool Authorization Flow:
User → Agent requests tool call
     ↓
Governance Layer checks: is this agent authorized for this tool?
     ↓ yes
MCP client sends request to MCP server
     ↓
MCP server executes tool + returns structured result
     ↓
Agent receives result → continues cognitive loop
```

---

### Layer 10 — Memory Layer

```
Memory Access Patterns:
───────────────────────

READ patterns (per agent):
┌─────────────────────────┬──────────────────────────────────────────┐
│ Agent                   │ Reads From                               │
├─────────────────────────┼──────────────────────────────────────────┤
│ Orchestrator            │ Redis (state), PostgreSQL (intake)       │
│ Market Intelligence     │ Qdrant (cached market data)              │
│ Audience Insight        │ PostgreSQL (brief), Qdrant (personas)    │
│ Launch Strategy         │ PostgreSQL (brief + personas)            │
│ Content Generation      │ PostgreSQL (all approved outputs)        │
│ Analytics & Feedback    │ PostgreSQL (KPIs), GA4/HubSpot via MCP  │
└─────────────────────────┴──────────────────────────────────────────┘

WRITE patterns (per agent):
┌─────────────────────────┬──────────────────────────────────────────┐
│ Agent                   │ Writes To                                │
├─────────────────────────┼──────────────────────────────────────────┤
│ Orchestrator            │ Redis (workflow state)                   │
│ Market Intelligence     │ Qdrant (embeddings), PostgreSQL (brief)  │
│ Audience Insight        │ Qdrant (persona vectors), PG (personas)  │
│ Launch Strategy         │ PostgreSQL (strategy)                    │
│ Content Generation      │ PostgreSQL (content per persona)         │
│ Analytics & Feedback    │ PostgreSQL (snapshots, recommendations)  │
└─────────────────────────┴──────────────────────────────────────────┘
```

**PostgreSQL Schema (core tables):**
```sql
users          (id, clerk_id, email, org_id, plan, created_at)
organisations  (id, name, plan, settings)
launches       (id, user_id, name, product_desc, goal, status, created_at)
briefs         (id, launch_id, competitors, trends, sources, approved_at)
personas       (id, launch_id, name, role, pains, jtbd, messaging, approved_at)
strategies     (id, launch_id, phases, milestones, channels, kpis, approved_at)
content        (id, launch_id, persona_id, type, body, approved_at)
analytics      (id, launch_id, metrics, recommendations, snapshot_at)
hitl_log       (id, launch_id, stage, decision, edited_output, decided_at)
agent_runs     (id, launch_id, agent_type, status, tokens, latency, created_at)
```

---

### Layer 11 — Guardrails & Governance

```
THREE GATES — every agent output passes all three:

GATE 1 — INPUT (before agent receives task)
├── PII scrubber          remove emails, phones, names
├── Injection detector    flag prompt injection patterns
├── Length validator      max 2,000 chars product description
└── Content policy        reject harmful/illegal requests

GATE 2 — TOOL EXECUTION (before MCP tool fires)
├── Scope check           agent authorized for this tool?
├── Parameter validator   inputs match MCP tool schema
├── Secret detector       no API keys/tokens in parameters
└── Rate check            within tool call budget

GATE 3 — OUTPUT (after agent generates result)
├── Pydantic validator    output matches required JSON schema
├── Citation enforcer     market claims need source URLs
├── Confidence threshold  flag low-confidence claims for HITL
├── Content safety        professional, brand-safe tone
├── XSS sanitizer         escape HTML before UI rendering
└── Hallucination score   cross-check facts against sources
```

---

### Layer 12 — Observability

```
FULL OBSERVABILITY STACK:
──────────────────────────

LangSmith — Agent Execution Tracing
  · Every agent run: inputs, CoT steps, tool calls, outputs
  · Token usage + cost per agent per launch
  · Latency breakdown per cognitive loop step
  · Tool call success/failure rates

Langfuse — Evaluation Pipeline
  · Output quality scores (automated + human)
  · Prompt A/B testing (which system prompt performs better)
  · Regression suite — new deployments tested against baselines
  · HITL edit rate tracking (how often users change agent outputs)

Sentry — Error Tracking
  · Backend exceptions (FastAPI, Celery, Lambda)
  · Frontend errors (React, Next.js)
  · Agent failures with full stack trace

PostHog — Product Analytics
  · User funnel: signup → first brief → paid
  · HITL conversion rates per stage
  · Feature adoption (which agents users engage most)
  · Session recordings (privacy-safe)

AWS CloudWatch — Infrastructure
  · Lambda health, invocation count, error rate
  · API Gateway latency (p50, p95, p99)
  · Celery queue depth (backlog alert > 50 tasks)
  · Redis memory usage

ALERT THRESHOLDS:
  · Agent failure rate > 5%         → PagerDuty (P1)
  · API p99 latency > 10s           → Slack alert (P2)
  · Celery queue depth > 50         → Slack alert (P2)
  · Hallucination score > 10%       → Langfuse flag (P2)
  · Token cost spike > 2x baseline  → Email alert (P3)
```

---

### Layer 13 — Infrastructure & Platform

```
INFRASTRUCTURE TOPOLOGY:
─────────────────────────

Vercel (Frontend)
  ├── Global edge deployment (100+ PoPs)
  ├── Preview deployments per PR
  ├── Environment variables (non-secret)
  └── Analytics + Web Vitals

AWS (Backend + Agents)
  ├── ECS Fargate — FastAPI API (always-on, auto-scaling)
  ├── Lambda — 6 agent functions (serverless, scale-to-zero)
  ├── S3 — exports, uploads, assets
  ├── Secrets Manager — all API keys
  ├── CloudWatch — logs + metrics + alerts
  └── VPC — private networking (Redis, Qdrant internal)

Managed Services
  ├── Supabase — PostgreSQL (managed, RLS, daily backups)
  ├── Qdrant Cloud — vector store (managed, EU region)
  └── Redis Cloud — cache + queue (managed, persistent)

CI/CD (GitHub Actions)
  ├── PR → lint + test + eval suite
  ├── Merge main → preview deploy (Vercel)
  ├── Tag (semver) → production deploy
  │     ├── Lambda blue/green deployment
  │     └── ECS rolling update
  └── Post-deploy → smoke tests + health checks
```

---

## 3. Request Flow — End to End

```
USER: "Run launch intelligence for my product"
         │
         ▼
[1] Browser → POST /api/v1/launches/{id}/run (HTTPS + JWT)
         │
         ▼
[2] Vercel Edge → auth middleware check → origin API
         │
         ▼
[3] FastAPI → validate JWT (Clerk) → rate limit check → sanitize input
         │
         ▼
[4] Celery → enqueue orchestrator task (Redis broker)
         │
         ▼
[5] Orchestrator Agent (Lambda) →
      load context from PostgreSQL
      write workflow plan to Redis
      dispatch Market Intelligence task (Celery)
         │
         ▼
[6] Market Intelligence Agent (Lambda) →
      Cognitive Loop:
        Perceive → load context
        Reason → plan search queries
        Act → Tavily MCP (3 web searches)
        Validate → citation check + schema validation
        Observe → quality score > threshold?
        Reflect → write to Qdrant + PostgreSQL
         │
         ▼
[7] Redis pub/sub → SSE endpoint → Next.js EventSource
      User SEES: competitor cards streaming in real time
         │
         ▼
[8] Orchestrator writes HITL_PENDING to Redis
      SSE pushes HITL checkpoint to browser
         │
         ▼
[9] User clicks [Approve]
      WebSocket → FastAPI → Redis state = APPROVED
         │
         ▼
[10] Orchestrator dispatches Audience Insight Agent
      [Pattern repeats for each agent...]
         │
         ▼
[11] All stages complete →
      Orchestrator synthesizes launch playbook
      PostgreSQL: launch status = COMPLETE
      SSE: final dashboard populated
         │
         ▼
[12] LangSmith: full trace logged
     Langfuse: quality scores computed
     PostHog: funnel event fired
     CloudWatch: metrics updated
```

---

## 4. Scalability Design

| Concern | Solution | Scale Target |
|---------|---------|-------------|
| Frontend traffic | Vercel Edge CDN | 100K concurrent users |
| API throughput | ECS Fargate auto-scaling | 1,000 req/sec |
| Agent concurrency | Lambda (burst: 3,000/region) | 500 concurrent launches |
| Memory read latency | Redis (in-memory, <1ms) | 10K ops/sec |
| Vector search latency | Qdrant (HNSW index) | <50ms p99 |
| Database connections | Supabase PgBouncer pooling | 10K connections |
| Queue throughput | Celery + Redis | 10K tasks/min |

---

## 5. Cost Architecture

| Component | Cost Model | Estimated (Early Stage) |
|-----------|-----------|------------------------|
| Claude API (tokens) | Per token | ~$0.15–0.30 per launch |
| AWS Lambda | Per invocation | ~$0.002 per launch |
| Vercel | Flat + usage | $20/month (Pro) |
| Supabase | Flat + storage | $25/month (Pro) |
| Qdrant Cloud | Per vector | $35/month (Starter) |
| Redis Cloud | Memory-based | $30/month (Essentials) |
| LangSmith | Per trace | $20/month (Plus) |
| Tavily API | Per search | ~$0.01 per launch |
| **Total (100 launches/month)** | | **~$200–250/month** |

**Unit economics at scale:**
- ARPU: $75/month
- COGS per active user: ~$8–12/month
- Gross margin target: **75–85%**
