# Case Study
## How I Built LaunchIQ: From Problem to Multi-Agent AI Product in 12 Weeks

**Author:** Venkata Anil Kumar — AI Engineer
**Date:** 2026-04-09

---

## The Problem I Couldn't Ignore

During conversations with startup founders and product marketers, I kept hearing the same frustration:

> *"I know what a good product launch looks like. I just don't have the time or team to execute one properly."*

The reality I observed:
- A solo founder at a Series A startup spending **18 hours a week** on launch research and planning — manually
- A product marketer at a 100-person SaaS company running 4 launches a year, each one starting with the same painful 2-week research cycle
- A growth marketer guessing at messaging because "we don't have budget for proper research"

The tools existed to solve pieces of this problem — Jasper for copy, Crayon for CI, HubSpot for execution — but nothing connected them with AI intelligence into a single, coherent launch workflow.

That gap became LaunchIQ.

---

## The Insight That Shaped Everything

Most "AI marketing tools" in 2026 are still fundamentally **prompt wrappers** — you ask a question, you get an answer. But a real launch requires sequential, contextual intelligence:

1. You need to understand the **market** before you can define an **audience**
2. You need to understand the **audience** before you can write a **strategy**
3. You need the **strategy** before content makes any sense

This isn't a single prompt problem. It's an **agent orchestration problem**.

That insight shaped every architectural decision: LaunchIQ would be a true multi-agent system where each agent has a specialization, shares context with downstream agents, and hands off to humans at the right moments.

---

## What I Built

### The System

A 6-agent AI platform built on Claude Agent SDK and MCP:

| Agent | Responsibility |
|-------|---------------|
| Orchestrator | Coordinates all agents, manages workflow state, synthesizes output |
| Market Intelligence | Autonomous web research — competitors, trends, market signals |
| Audience Insight | Buyer persona generation with messaging angles |
| Launch Strategy | Phased GTM plan with milestones and KPIs |
| Content Generation | Strategy-aware copy for email, social, and ads |
| Analytics & Feedback | Post-launch performance monitoring and optimization |

### The Architecture Decision I'm Most Proud Of: HITL as First-Class Workflow

Most AI tools treat human review as a post-processing step — the AI generates, human reads. I flipped this.

In LaunchIQ, **Human-in-the-Loop (HITL) checkpoints are structural workflow steps.** The agent pipeline literally pauses, pushes output to the UI via Server-Sent Events, and waits for user approval before the next agent runs.

This wasn't just a UX decision — it required careful async architecture:
- Agent state stored in Redis with workflow status flags
- WebSocket connection maintained through agent pause periods
- Approval events trigger pipeline resume via Celery task signals

The result: users feel in control of an AI that's doing real work for them, not just generating text they have to validate from scratch.

### The Hardest Technical Problem: Agent Memory

Deciding what each agent remembers, how long it persists, and how downstream agents access upstream context took the most iteration.

Final memory architecture:
- **Redis:** Session-scoped agent scratchpads and workflow state (TTL: 24h)
- **Qdrant:** Market research embeddings and competitor vectors (persistent, refreshable)
- **PostgreSQL:** Approved outputs — personas, strategies, content — referenced by downstream agents

The key insight: agents don't pass data to each other directly. They write to shared persistent stores, and each downstream agent reads what it needs. This decouples agents and makes the system resilient to individual agent failures.

---

## The Challenges I Navigated

### Challenge 1: Structured Output Reliability

Getting Claude to reliably output parseable JSON schemas for each agent's output took 10–15 iterations per agent. The solution: Pydantic validation at the output layer with graceful fallback — if the schema doesn't parse, the orchestrator retries with a stricter prompt variant.

### Challenge 2: Streaming Agent Output to the Browser

Real-time agent output (users watching the market brief populate live) required:
- FastAPI async generator streaming to Celery worker
- SSE (Server-Sent Events) from backend to Next.js frontend
- React 19 concurrent rendering for smooth streaming UI

The challenge was maintaining the SSE connection while Celery workers ran in separate processes. Solved with Redis pub/sub as the bridge between Celery and the SSE endpoint.

### Challenge 3: Prompt Engineering for Context Handoff

Each agent needs context from previous agents without exceeding token limits. The solution: structured context summaries — the orchestrator generates a compressed context object after each HITL approval, containing only what the next agent needs. This keeps prompts focused and costs manageable.

### Challenge 4: Solo Founder Prioritization

With no team, I had to decide what to build and what to defer. My prioritization framework:
- Build only what validates the core hypothesis: *"Can agents deliver a better launch brief than manual research in < 10 minutes?"*
- Defer everything that doesn't answer that question (integrations, collaboration, mobile)
- Build observability (LangSmith traces, Langfuse evals) from day one — agent quality is invisible without it

---

## The Results

| Metric | Result |
|--------|--------|
| Time to first launch brief | **< 10 minutes** (target: < 10 min) |
| Agent task completion rate | **92%** (target: > 90%) |
| Average user edit rate on agent outputs | **22%** (target: < 30%) |
| Pilot user NPS | **47** (target: > 40) |
| Pilot user quote | *"This is genuinely the first AI tool that gave me something I could use immediately, not just something I had to fix."* |

---

## What Hiring Managers Should Take From This

**1. I design systems, not prompts.**
LaunchIQ's value isn't in clever prompts — it's in the architectural decisions around memory, HITL, agent coordination, and observability that make the system reliable and trustworthy.

**2. I think about the full product, not just the AI layer.**
Building LaunchIQ required PRDs, user research, competitive analysis, GTM strategy, security design, and onboarding design — not just agent engineering.

**3. I move fast without cutting corners on quality.**
12 weeks. Solo. 6 agents. 16 product documents. Working demo. Security design. GDPR-aware. This is how I approach any engineering challenge.

**4. I've already solved the hardest AI engineering problems you're hiring for.**
Async agent orchestration. Memory architecture. Structured output reliability. Streaming UI. HITL workflows. Agent evaluation. If these are on your roadmap, I've already built them.

---

## What's Next for LaunchIQ

- Content Generation Agent (complete)
- Analytics & Feedback Agent (complete)
- HubSpot + Slack integrations (Phase 2)
- Public beta launch on Product Hunt
- 10 paying customers by Month 3

---

*Venkata Anil Kumar — AI Engineer*
*Building the future of intelligent product launches.*
*Open to full-time roles where I can bring this level of depth to your product.*
