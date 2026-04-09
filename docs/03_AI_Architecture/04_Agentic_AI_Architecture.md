# Agentic AI Architecture — LaunchIQ
## Designed Against 2026 Industry Patterns (Anthropic · OpenAI · Google · AWS · Azure)

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09
**References:** `03_Agentic_AI_References_2026.md`

---

## 1. Architecture Philosophy

LaunchIQ is a **2026-native agentic AI system** — designed against the patterns published by Anthropic, OpenAI, Google, AWS, and Azure in 2026.

The core philosophy borrows from the best of each platform:

| Principle | Borrowed From | Applied in LaunchIQ |
|-----------|--------------|---------------------|
| Simple, composable patterns first | Anthropic | 6 focused agents, each with one job |
| Agent = LLM + instructions + tools + memory | OpenAI | Every agent has a defined identity, scope, and toolset |
| Cognitive loop: Perceive → Reason → Act | AWS AgentCore | Each agent runs this loop per task |
| Policy controls outside the reasoning loop | AWS AgentCore | Guardrails layer validates before tool execution |
| Stateful threads + managed execution | Azure Foundry | Redis workflow state + HITL checkpoint system |
| Native tool use + thinking mode | Google ADK | Claude thinking mode + MCP tool registry |
| Governance as a first-class concern | Azure + AWS | Every agent action is auditable and reversible |

> **Design rule:** Start with the simplest pattern that works. Add complexity only when the simpler pattern provably fails.

---

## 2. Full System Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          LAUNCHIQ AGENTIC SYSTEM                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │                        USER INTERFACE LAYER                         │   ║
║  │            Next.js 15 · React 19 · Tailwind · shadcn/ui             │   ║
║  │      Real-time agent streaming via SSE · HITL checkpoint UI         │   ║
║  └─────────────────────────────┬────────────────────────────────────────┘   ║
║                                │ HTTPS / SSE / WebSocket                    ║
║  ┌─────────────────────────────▼────────────────────────────────────────┐   ║
║  │                      API GATEWAY LAYER                              │   ║
║  │                   FastAPI (Python 3.12) — Async                     │   ║
║  │        Clerk JWT Auth · Rate Limiting · Input Sanitization          │   ║
║  └──────────────┬──────────────────────┬──────────────────────────────-┘   ║
║                 │                      │                                     ║
║                 │ Enqueue              │ Stream results                      ║
║  ┌──────────────▼──────┐  ┌───────────▼──────────────────────────────────┐  ║
║  │  TASK QUEUE         │  │         GOVERNANCE LAYER                     │  ║
║  │  Celery + Redis     │  │  Policy checks BEFORE tool execution         │  ║
║  │                     │  │  (AWS AgentCore Policy pattern)              │  ║
║  │  Agent tasks run    │  │  · Input validation (Pydantic)               │  ║
║  │  async, isolated    │  │  · Tool permission scope check               │  ║
║  │  per launch         │  │  · Output schema validation                  │  ║
║  └──────────────┬──────┘  │  · Hallucination guard (citation check)      │  ║
║                 │          │  · PII scrubber before agent sees input      │  ║
║                 │          └──────────────────────────────────────────────┘  ║
║                 │                                                             ║
║  ┌──────────────▼──────────────────────────────────────────────────────────┐ ║
║  │                    ORCHESTRATOR AGENT                                   │ ║
║  │                    Claude Opus 4.6                                      │ ║
║  │                                                                         │ ║
║  │  Pattern: Orchestrator-Workers (Anthropic) + Runner (OpenAI)           │ ║
║  │                                                                         │ ║
║  │  · Decomposes user goal → sub-tasks                                     │ ║
║  │  · Dispatches sub-agents via A2A protocol                               │ ║
║  │  · Manages workflow state in Redis (Azure Threads pattern)              │ ║
║  │  · Synthesizes final launch playbook from all agent outputs             │ ║
║  │  · Routes to HITL gateway at each major checkpoint                      │ ║
║  │  · Retries failed sub-agents with variant prompts (OpenAI Runner)       │ ║
║  └──────┬──────────┬──────────────┬────────────────┬────────────────────────┘ ║
║         │          │              │                │                           ║
║  ┌──────▼───┐ ┌────▼──────┐ ┌────▼──────┐  ┌──────▼──────┐  ┌─────────────┐ ║
║  │ MARKET   │ │ AUDIENCE  │ │ LAUNCH    │  │ CONTENT     │  │ ANALYTICS   │ ║
║  │ INTEL    │ │ INSIGHT   │ │ STRATEGY  │  │ GENERATION  │  │ FEEDBACK    │ ║
║  │ AGENT    │ │ AGENT     │ │ AGENT     │  │ AGENT       │  │ AGENT       │ ║
║  │          │ │           │ │           │  │             │  │             │ ║
║  │Sonnet4.6 │ │ Sonnet4.6 │ │ Opus 4.6  │  │ Sonnet 4.6  │  │ Haiku 4.5   │ ║
║  └──────┬───┘ └────┬──────┘ └────┬──────┘  └──────┬──────┘  └──────┬──────┘ ║
║         │          │              │                │                │         ║
║  ┌──────▼──────────▼──────────────▼────────────────▼────────────────▼───────┐ ║
║  │                    COGNITIVE LOOP (per agent)                           │ ║
║  │         Perceive → Reason (CoT) → Plan → Act → Observe → Reflect       │ ║
║  │                    (AWS AgentCore + Google Thinking Mode)               │ ║
║  └──────────────────────────────┬──────────────────────────────────────────┘ ║
║                                 │                                             ║
║  ┌──────────────────────────────▼──────────────────────────────────────────┐  ║
║  │                       TOOL REGISTRY (MCP)                              │  ║
║  │           Model Context Protocol — Universal tool standard             │  ║
║  │                                                                        │  ║
║  │  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │  ║
║  │  │  Tavily    │ │ HubSpot  │ │  Slack   │ │   GA4    │ │  Email    │  │  ║
║  │  │  Search    │ │   MCP    │ │   MCP    │ │   MCP    │ │ Platform  │  │  ║
║  │  │  MCP       │ │          │ │          │ │          │ │   MCP     │  │  ║
║  │  └────────────┘ └──────────┘ └──────────┘ └──────────┘ └───────────┘  │  ║
║  └──────────────────────────────┬──────────────────────────────────────────┘  ║
║                                 │                                             ║
║  ┌──────────────────────────────▼──────────────────────────────────────────┐  ║
║  │                        MEMORY LAYER                                    │  ║
║  │                                                                        │  ║
║  │  Short-term (Redis)    Long-term (Qdrant)    Structured (PostgreSQL)   │  ║
║  │  · Session state       · Market embeddings   · Users, launches         │  ║
║  │  · Agent scratchpad    · Competitor vectors  · Strategies, personas    │  ║
║  │  · HITL decisions      · Persona vectors     · Content, analytics      │  ║
║  │  · Task queue          · Brand voice         · Audit logs              │  ║
║  └──────────────────────────────┬──────────────────────────────────────────┘  ║
║                                 │                                             ║
║  ┌──────────────────────────────▼──────────────────────────────────────────┐  ║
║  │                     OBSERVABILITY LAYER                                │  ║
║  │   LangSmith (traces) · Langfuse (evals) · Sentry · PostHog            │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. Agent Architecture Pattern

LaunchIQ follows the **Orchestrator-Workers** pattern (Anthropic) combined with the **Agent = LLM + Instructions + Tools + Memory + Behavior** identity model (OpenAI).

### 3.1 Agent Identity Model (OpenAI Pattern)

Every agent in LaunchIQ is defined by 5 components:

```
Agent Identity
├── Instructions   → System prompt defining role, scope, constraints, output format
├── Model          → Claude Opus 4.6 / Sonnet 4.6 / Haiku 4.5 (task-matched)
├── Tools          → MCP tools scoped specifically to this agent's domain
├── Memory         → What this agent reads from and writes to
└── Behavior       → Retry policy, fallback strategy, HITL trigger conditions
```

### 3.2 Agent Definitions

#### Orchestrator Agent
```
Model:        Claude Opus 4.6
Pattern:      Orchestrator-Workers (Anthropic) + Runner (OpenAI)
Instructions: Master coordinator. Decompose user goal. Dispatch agents.
              Manage state. Synthesize. Never perform domain tasks directly.
Tools:        None (dispatches to sub-agents only)
Memory Read:  PostgreSQL (user intake), Redis (workflow state)
Memory Write: Redis (workflow plan, agent status, HITL decisions)
Behavior:     Retry sub-agent on failure (max 2). Escalate to user on 3rd failure.
```

#### Market Intelligence Agent
```
Model:        Claude Sonnet 4.6
Pattern:      ReAct loop — Search → Analyze → Structure → Output
Instructions: You are a market research specialist. Research competitors and
              trends for the given product. Use Tavily search. Cite all sources.
              Output structured competitive brief. Never fabricate market data.
Tools:        Tavily Search MCP, HTML Scraper MCP
Memory Read:  Qdrant (cached market data for similar products)
Memory Write: Qdrant (new competitor vectors), PostgreSQL (brief record)
Behavior:     If search fails → use cached Qdrant data + flag as stale.
              Require citation for every competitive claim.
```

#### Audience Insight Agent
```
Model:        Claude Sonnet 4.6
Pattern:      Chain of Thought — derive personas from market brief context
Instructions: You are a buyer persona specialist. Build 3 distinct personas
              using the market brief as context. Apply JTBD framework.
              Each persona needs: role, pains, goals, JTBD, messaging angle.
Tools:        Persona template MCP resource
Memory Read:  PostgreSQL (market brief), Qdrant (similar persona patterns)
Memory Write: PostgreSQL (approved personas), Qdrant (persona embeddings)
Behavior:     If 3 distinct personas cannot be differentiated → generate 2
              and prompt user to refine target market.
```

#### Launch Strategy Agent
```
Model:        Claude Opus 4.6 (highest reasoning — strategic decisions)
Pattern:      Plan-and-Execute — full strategy plan before any output
Instructions: You are a GTM strategist. Generate a 3-phase launch plan
              (pre-launch, launch, post-launch) grounded in the personas
              and competitive brief. Every recommendation must be specific
              and actionable with defined success metrics.
Tools:        GTM framework library MCP, Calendar MCP
Memory Read:  PostgreSQL (brief + personas), Qdrant (strategy patterns)
Memory Write: PostgreSQL (strategy record)
Behavior:     Default timeline: 4-week pre-launch, 1-week launch, 4-week post.
              Override if user specifies launch date.
```

#### Content Generation Agent
```
Model:        Claude Sonnet 4.6
Pattern:      Prompt Chaining — strategy context → persona context → generate
Instructions: You are a launch copywriter. Generate strategy-aware content
              for each persona. Content must reflect the approved strategy
              and speak directly to each persona's pain points and JTBD.
              No generic copy. Every piece must be persona-attributed.
Tools:        Brand voice analyzer MCP, Tone checker MCP
Memory Read:  PostgreSQL (all approved outputs: brief, personas, strategy)
Memory Write: PostgreSQL (content record per persona)
Behavior:     Generate 1 content format if full suite times out.
              Retry remainder async. Flag completion to Orchestrator.
```

#### Analytics & Feedback Agent
```
Model:        Claude Haiku 4.5 (speed + cost — high-frequency monitoring)
Pattern:      Evaluator-Optimizer — monitor → evaluate → recommend
Instructions: You are a launch performance analyst. Monitor metrics against
              the defined launch KPIs. Surface anomalies. Generate top 3
              optimization recommendations. Be specific — no generic advice.
Tools:        GA4 MCP, HubSpot MCP, Email platform MCP
Memory Read:  PostgreSQL (launch KPIs, historical baselines)
Memory Write: PostgreSQL (analytics snapshots, recommendations log)
Behavior:     If live data unavailable → surface last known + timestamp.
              Alert Orchestrator if KPI deviation > 20%.
```

---

## 4. Cognitive Loop (Per Agent)

Borrowed from **AWS AgentCore** (Perception → Reasoning → Execution) and **Google Gemini Thinking Mode**, every LaunchIQ agent runs the same cognitive loop:

```
┌─────────────────────────────────────────────────────────┐
│                  AGENT COGNITIVE LOOP                   │
│                                                         │
│   1. PERCEIVE                                           │
│      Read task from Orchestrator (A2A message)          │
│      Load context from Memory Layer                     │
│      Retrieve relevant knowledge from Qdrant (RAG)      │
│                   ↓                                     │
│   2. REASON (Chain of Thought — internal)               │
│      Analyze the task against loaded context            │
│      Identify what tools are needed                     │
│      Plan the execution steps                           │
│      [Claude thinking mode — not shown to user]         │
│                   ↓                                     │
│   3. ACT                                                │
│      Execute tool calls via MCP (web search, APIs)      │
│      Process tool results                               │
│      Generate structured output (Pydantic schema)       │
│                   ↓                                     │
│   4. VALIDATE (Governance Layer)                        │
│      Schema validation (Pydantic)                       │
│      Citation check (market claims need sources)        │
│      Safety filter (content policy)                     │
│      PII check (no customer data in outputs)            │
│                   ↓                                     │
│   5. OBSERVE                                            │
│      Did the output meet quality thresholds?            │
│      If NO → reflect and retry (max 2 retries)          │
│      If YES → write to memory + notify Orchestrator     │
│                   ↓                                     │
│   6. REFLECT (Self-correction)                          │
│      Compare output against task requirements           │
│      Flag uncertainty → escalate to HITL if needed      │
│      Write learned context to memory                    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Planning & Reasoning Patterns

LaunchIQ uses different reasoning patterns per agent based on task complexity:

| Agent | Reasoning Pattern | Why |
|-------|-----------------|-----|
| Orchestrator | **Plan-and-Execute** | Must plan full workflow before dispatching — prevents redundant agent runs |
| Market Intelligence | **ReAct** (Reason + Act loop) | Search → analyze → search more if gaps found — iterative research |
| Audience Insight | **Chain of Thought** | Step-by-step persona derivation from market brief |
| Launch Strategy | **Tree of Thought** | Explore multiple strategy paths, select strongest |
| Content Generation | **Prompt Chaining** | Context layers built up: brief → personas → strategy → copy |
| Analytics & Feedback | **Evaluator-Optimizer** | One pass evaluates metrics, second pass generates recommendations |

---

## 6. Memory Architecture

Borrowed from **Azure Managed Memory** (auto extraction + retrieval) and **AWS AgentCore Memory** (cross-session retention):

```
┌──────────────────────────────────────────────────────────────┐
│                    LAUNCHIQ MEMORY STACK                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  IN-CONTEXT MEMORY (Claude context window)           │    │
│  │  · Current task + immediate agent scratchpad         │    │
│  │  · Compressed context summary from Orchestrator      │    │
│  │  · Active HITL decision state                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                            ↕ read/write                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  SHORT-TERM MEMORY — Redis (TTL: 24h)                │    │
│  │  · Workflow state per launch (Orchestrator owned)    │    │
│  │  · Agent run status (pending/running/complete/error) │    │
│  │  · HITL pause state (waiting for user approval)      │    │
│  │  · Agent scratchpad per session                      │    │
│  │  · Rate limit counters per user                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                            ↕ read/write                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  LONG-TERM MEMORY — Qdrant (Vector Store)            │    │
│  │  · Market intelligence embeddings (per industry)     │    │
│  │  · Competitor profile vectors (refreshed monthly)    │    │
│  │  · Approved persona embeddings (per product type)    │    │
│  │  · Brand voice vectors (per user — learned over time)│    │
│  │  · Strategy pattern library (successful GTM plans)   │    │
│  └──────────────────────────────────────────────────────┘    │
│                            ↕ read/write                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  STRUCTURED MEMORY — PostgreSQL (Supabase)           │    │
│  │  · User accounts + org settings                      │    │
│  │  · Launch records (all user launches)                │    │
│  │  · Approved outputs (briefs, personas, strategies)   │    │
│  │  · Generated content (email, social, ads)            │    │
│  │  · Analytics snapshots + recommendation history      │    │
│  │  · HITL decision audit log (immutable)               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  CONTEXT HANDOFF SCHEMA (between agents)                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  {                                                   │    │
│  │    launch_id: uuid,                                  │    │
│  │    product_summary: str (max 500 tokens),            │    │
│  │    completed_stages: list[str],                      │    │
│  │    market_brief_ref: postgres_id,                    │    │
│  │    personas_ref: postgres_id,                        │    │
│  │    strategy_ref: postgres_id,                        │    │
│  │    hitl_decisions: list[decision_record]             │    │
│  │  }                                                   │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Context budget rule:** Each agent receives a compressed context object (max 2,000 tokens) — not the full conversation history. This keeps token costs predictable and prevents context overflow.

---

## 7. Tool Registry — MCP Architecture

Borrowed from **Anthropic MCP** (universal tool standard) and **Azure Tools Tab** (unified tool discovery):

```
┌───────────────────────────────────────────────────────────────┐
│                  LAUNCHIQ MCP TOOL REGISTRY                   │
│                                                               │
│  Tool Registry (manifest of all available tools)             │
│  Each agent declares which tools it is authorized to use      │
│                                                               │
│  ┌─────────────────┬────────────────────┬──────────────────┐  │
│  │  TOOL           │  AUTHORIZED AGENTS │  MCP SERVER      │  │
│  ├─────────────────┼────────────────────┼──────────────────┤  │
│  │ web_search      │ Market Intel       │ Tavily MCP       │  │
│  │ html_scraper    │ Market Intel       │ Custom MCP       │  │
│  │ persona_templates│ Audience Insight  │ Internal MCP     │  │
│  │ gtm_frameworks  │ Launch Strategy    │ Internal MCP     │  │
│  │ calendar        │ Launch Strategy    │ Google Cal MCP   │  │
│  │ brand_voice     │ Content Gen        │ Internal MCP     │  │
│  │ tone_checker    │ Content Gen        │ Internal MCP     │  │
│  │ hubspot_contacts│ Content, Analytics │ HubSpot MCP      │  │
│  │ slack_notify    │ Orchestrator       │ Slack MCP        │  │
│  │ ga4_events      │ Analytics          │ GA4 MCP          │  │
│  │ email_metrics   │ Analytics          │ Loops/Mailchimp  │  │
│  └─────────────────┴────────────────────┴──────────────────┘  │
│                                                               │
│  Tool Authorization: Governance Layer checks agent's tool     │
│  scope BEFORE execution — no agent can call tools outside     │
│  its declared manifest (AWS AgentCore Policy pattern)         │
└───────────────────────────────────────────────────────────────┘
```

---

## 8. HITL Architecture (Human-in-the-Loop)

Borrowed from **Anthropic Plan Mode** and **Azure Managed Runs** — HITL is a structural workflow step, not a UX layer.

```
┌──────────────────────────────────────────────────────────────┐
│                    HITL WORKFLOW ENGINE                      │
│                                                              │
│  Agent completes task                                        │
│         ↓                                                    │
│  Orchestrator writes HITL_PENDING to Redis                   │
│  (workflow state = PAUSED)                                   │
│         ↓                                                    │
│  Output streamed to frontend via SSE                         │
│  (user sees agent result in real time)                       │
│         ↓                                                    │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  USER DECISION (3 options)                            │   │
│  │  [✓ Approve]  →  Resume pipeline                      │   │
│  │  [✎ Edit]     →  User modifies output → re-approve    │   │
│  │  [↺ Regenerate] → Re-run agent with feedback prompt   │   │
│  └───────────────────────────────────────────────────────┘   │
│         ↓                                                    │
│  Decision written to PostgreSQL audit log (immutable)        │
│  Redis state updated to APPROVED / REGENERATE                │
│  Orchestrator resumes pipeline                               │
│                                                              │
│  HITL CHECKPOINTS IN LAUNCHIQ                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  1. Post Market Brief      (before persona agent)    │    │
│  │  2. Post Personas          (before strategy agent)   │    │
│  │  3. Post Strategy          (before content agent)    │    │
│  │  4. Post Content           (before execution tracker)│    │
│  │  5. Post Analytics Recs    (before acting on data)   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  AUTONOMY DIAL (user-configurable)                           │
│  Level 1: Approve every step (default — new users)          │
│  Level 2: Approve strategy + content only                   │
│  Level 3: Notify only on major decisions                    │
│  Level 4: Full autonomous (power users — opt-in)            │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Workflow Patterns

LaunchIQ uses **Sequential Pipeline** as the primary pattern with **Parallelization** for independent sub-tasks:

```
PRIMARY WORKFLOW — Sequential Pipeline (Anthropic pattern)
══════════════════════════════════════════════════════════

User Input
    │
    ▼
[Orchestrator: Plan-and-Execute]
    │
    ├──► Market Intelligence Agent ──► HITL ──┐
    │                                         │ context passed
    ├──► Audience Insight Agent ◄─────────────┘
    │         │                               
    │         └──► HITL ────────────────────┐
    │                                       │ context passed
    ├──► Launch Strategy Agent ◄────────────┘
    │         │                              
    │         └──► HITL ────────────────────┐
    │                                       │ context passed
    ├──► Content Generation Agent ◄─────────┘
    │         │                              
    │         └──► HITL ───────────────────────► Dashboard
    │
    └──► Analytics & Feedback Agent [post-launch, async]


PARALLEL EXECUTION — where applicable
═══════════════════════════════════════

Content Generation Agent runs 3 persona threads in parallel:
    ├──► Persona 1 content (email + social + ads) ─┐
    ├──► Persona 2 content (email + social + ads) ──┼──► Merge → approve
    └──► Persona 3 content (email + social + ads) ─┘


EVALUATOR-OPTIMIZER — Analytics Agent
═══════════════════════════════════════

Metrics pulled from GA4 + HubSpot
    ├──► Evaluator pass: compare vs launch KPIs
    └──► Optimizer pass: generate top 3 recommendations
```

---

## 10. Context Management

Borrowed from **Google's long-context strategy** and **Anthropic's context engineering**:

| Principle | Implementation |
|-----------|---------------|
| **Context budget per agent** | Max 2,000 tokens of context passed per agent (compressed) |
| **Selective context** | Each agent receives only what it needs — not full history |
| **Compression at handoff** | Orchestrator compresses prior outputs before passing to next agent |
| **RAG for knowledge** | Market data retrieved from Qdrant — not stuffed into prompts |
| **Schema as context** | Pydantic output schemas defined in system prompt — enforces structure |
| **Token cost tracking** | LangSmith tracks token usage per agent per launch |

**Context handoff example:**
```python
# What the Launch Strategy Agent receives (not the full raw brief)
context = {
    "product_summary": "LaunchIQ is an AI-powered...",  # 200 tokens
    "top_competitors": ["HubSpot", "Jasper", "Copy.ai"],  # 50 tokens
    "key_differentiator": "Multi-agent, end-to-end, < 10 min",  # 30 tokens
    "personas": [persona_1_summary, persona_2_summary, persona_3_summary],  # 300 tokens
    "launch_goal": "awareness + signups",  # 10 tokens
    "launch_timeline": "8 weeks"  # 5 tokens
}
# Total: ~600 tokens — focused, not bloated
```

---

## 11. Guardrails & Safety Layer

Borrowed from **OpenAI Guardrails**, **AWS AgentCore Policy**, and **Azure Governance Toolkit**:

```
INPUT GUARDRAILS (before agent sees user input)
├── PII scrubber — strip emails, names, phone numbers
├── Prompt injection detector — flag suspicious patterns
├── Input length limiter — max 2,000 chars for product description
└── Content policy check — reject harmful requests

TOOL EXECUTION GUARDRAILS (before MCP tool runs)
├── Tool scope check — agent authorized for this tool?
├── Parameter validation — tool inputs match expected schema
├── Rate limit check — within allowed tool call budget
└── Sensitive data check — no secrets passed to external APIs

OUTPUT GUARDRAILS (after agent generates output)
├── Pydantic schema validation — output matches required structure
├── Citation enforcer — market claims must have source URLs
├── Hallucination detector — flag low-confidence factual claims
├── Content safety filter — brand-safe, professional tone
└── XSS sanitizer — all outputs sanitized before UI rendering
```

---

## 12. Observability Architecture

Borrowed from **AWS OpenTelemetry** and **Anthropic LangSmith**:

```
WHAT IS TRACED PER AGENT RUN
├── Agent identity + model used
├── Input received (compressed)
├── Reasoning steps (CoT — internal only)
├── Tool calls + parameters + results
├── Memory reads (what was retrieved)
├── Memory writes (what was stored)
├── Output generated + schema validation result
├── Token usage (input + output + cost)
├── Latency per step
├── HITL decisions (approve / edit / regenerate)
└── Retry count + failure reasons

OBSERVABILITY STACK
├── LangSmith    → Agent traces, tool call graphs, token costs
├── Langfuse     → Output quality evals, prompt A/B tests, regression
├── Sentry       → Backend exceptions, frontend errors
├── PostHog      → User flows, HITL conversion rates, feature adoption
└── CloudWatch   → Lambda health, API latency, queue depth
```

**Eval framework (Langfuse):**

| Agent | Eval Metric | Pass Threshold |
|-------|------------|---------------|
| Market Intelligence | Research relevance score | > 0.80 |
| Market Intelligence | Hallucination rate | < 5% |
| Audience Insight | Persona specificity score | > 0.75 |
| Launch Strategy | Strategy completeness | > 0.85 |
| Content Generation | Persona alignment score | > 0.80 |
| Content Generation | User edit rate | < 30% |
| Analytics | Recommendation acceptance rate | > 50% |

---

## 13. Deployment Architecture

Borrowed from **AWS Serverless Lambda** and **Anthropic Managed Agents** (sandboxed execution):

```
┌──────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT TOPOLOGY                        │
│                                                              │
│  Vercel (Edge CDN)                                           │
│  └── Next.js 15 frontend — deployed globally                 │
│                                                              │
│  AWS Lambda (Serverless)                                     │
│  ├── Orchestrator Agent function (512MB, 15min timeout)      │
│  ├── Market Intelligence function (256MB, 5min timeout)      │
│  ├── Audience Insight function (256MB, 3min timeout)         │
│  ├── Launch Strategy function (512MB, 5min timeout)          │
│  ├── Content Generation function (256MB, 5min timeout)       │
│  └── Analytics function (128MB, 2min timeout)               │
│                                                              │
│  FastAPI on AWS ECS (always-on API gateway)                  │
│  ├── Handles auth, routing, rate limiting                    │
│  └── Manages Celery task queue → Lambda invocations         │
│                                                              │
│  Managed Services                                            │
│  ├── Supabase (PostgreSQL) — managed, RLS, backups           │
│  ├── Qdrant Cloud — managed vector store                     │
│  └── Redis Cloud — managed cache + queue                    │
│                                                              │
│  CI/CD (GitHub Actions)                                      │
│  ├── PR → run evals + tests                                  │
│  ├── Merge to main → deploy frontend to Vercel              │
│  └── Tag → deploy agents to Lambda (blue/green)             │
└──────────────────────────────────────────────────────────────┘
```

---

## 14. Pattern-to-Platform Mapping

How LaunchIQ maps to each platform's 2026 patterns:

| LaunchIQ Design | Pattern | Platform Source |
|----------------|---------|----------------|
| Orchestrator-Workers architecture | Orchestrator-Workers | Anthropic |
| MCP for all tool integrations | MCP protocol | Anthropic |
| Agent = LLM + instructions + tools + memory | Agent identity model | OpenAI |
| Retry + fallback in Orchestrator | Runner pattern | OpenAI |
| Handoffs via A2A context objects | Handoffs | OpenAI |
| Cognitive loop per agent | AgentCore cognitive loop | AWS |
| Governance layer before tool execution | AgentCore Policy | AWS |
| RAG for market knowledge | Knowledge Bases | AWS |
| Redis workflow state + HITL pause/resume | Threads + Runs | Azure |
| Managed long-term memory (Qdrant) | Managed Memory | Azure |
| Audit log for all agent actions | Governance Toolkit | Azure |
| Chain of Thought + Thinking Mode | Thinking Mode | Google |
| Compressed context handoff between agents | Context Engineering | Anthropic |
| Evaluator-Optimizer for Analytics Agent | Evaluator-Optimizer | Anthropic |
| Parallelization for content generation | Parallelization | Anthropic |
| LangSmith + Langfuse observability | OpenTelemetry standard | AWS |

---

## 15. Architecture Evolution Roadmap

| Phase | Architecture Addition | Pattern |
|-------|----------------------|---------|
| **Now (MVP)** | 6 agents + sequential pipeline + HITL | Orchestrator-Workers |
| **Phase 2** | Parallel content generation + integrations | Parallelization |
| **Phase 3** | Cross-session memory + brand voice learning | Managed Memory (Azure) |
| **Phase 4** | Full autonomy mode + governance dial | AgentCore Policy (AWS) |
| **Phase 5** | Multi-user team memory + org-level knowledge base | Shared Memory |

---

*This architecture is designed to evolve. Each phase adds one pattern — never rewrite, always extend.*

**References:** `docs/04_AI_Architecture/03_Agentic_AI_References_2026.md`
