# Agent Capability Matrix
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## Overview

LaunchIQ is powered by 6 specialized AI agents coordinated by an Orchestrator. This document details the exact capability, tools, inputs, outputs, and evaluation criteria for each agent.

---

## Agent Summary Table

| Agent | Model | Primary Role | Key Output |
|-------|-------|-------------|-----------|
| Orchestrator | Claude Opus 4.6 | Coordinates all agents, manages workflow | Workflow state, agent dispatch |
| Market Intelligence | Claude Sonnet 4.6 | Market & competitor research | Competitive brief + trend signals |
| Audience Insight | Claude Sonnet 4.6 | Buyer persona development | 3 personas with messaging angles |
| Launch Strategy | Claude Opus 4.6 | GTM plan creation | Phased launch strategy |
| Content Generation | Claude Sonnet 4.6 | Launch copy writing | Email, social, ad copy |
| Analytics & Feedback | Claude Haiku 4.5 | Performance monitoring | Optimization recommendations |

---

## 1. Orchestrator Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Opus 4.6 |
| **Role** | Master coordinator and workflow planner |
| **Trigger** | User submits product intake form |
| **Inputs** | Product description, target market, competitor names, launch goal |
| **Capabilities** | Task decomposition, agent dispatch, state management, synthesis |
| **Tools Used** | None directly — dispatches to sub-agents via A2A protocol |
| **Outputs** | Workflow execution plan, agent dispatch instructions, final brief compilation |
| **Memory** | Full session state, user preferences, HITL decision history |
| **HITL** | Surfaces summary after all agents complete for final review |
| **Eval Metrics** | Workflow completion rate, agent coordination efficiency, error recovery rate |
| **Error Handling** | Retry failed sub-agents, escalate to user if 2+ retries fail |

---

## 2. Market Intelligence Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Sonnet 4.6 |
| **Role** | Autonomous market researcher |
| **Trigger** | Dispatched by Orchestrator after intake |
| **Inputs** | Product description, competitor names (optional), target industry |
| **Capabilities** | Web research, competitor analysis, trend identification, market sizing |
| **Tools Used** | Tavily Search API, HTML scraper, news aggregator, Qdrant (vector retrieval) |
| **Outputs** | Competitive landscape (4–6 competitors), trend signals (5–8 trends), market brief |
| **Memory** | Caches research results in Qdrant for reuse across sessions |
| **HITL** | User reviews and approves competitive brief before next agent runs |
| **Eval Metrics** | Research relevance score, competitor coverage accuracy, hallucination rate |
| **Latency Target** | < 90 seconds for full research cycle |
| **Error Handling** | Fallback to cached data if live search fails; flag to user if data is stale |

---

## 3. Audience Insight Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Sonnet 4.6 |
| **Role** | Buyer persona specialist |
| **Trigger** | Dispatched after Market Intelligence HITL approval |
| **Inputs** | Product description, market brief (from Market Intelligence Agent), target industry |
| **Capabilities** | Persona synthesis, segment mapping, JTBD analysis, messaging angle generation |
| **Tools Used** | Persona template library (MCP resource), market brief context |
| **Outputs** | 3 buyer personas — each with: demographics, goals, pain points, JTBD, messaging angle |
| **Memory** | Stores approved personas in PostgreSQL for content agent context |
| **HITL** | User can edit persona details (name, role, pain points) before approval |
| **Eval Metrics** | Persona specificity score, messaging relevance, user edit rate |
| **Latency Target** | < 45 seconds |
| **Error Handling** | Generate 2 personas if 3 cannot be differentiated; prompt user to refine target market |

---

## 4. Launch Strategy Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Opus 4.6 |
| **Role** | GTM strategist |
| **Trigger** | Dispatched after Audience Insight HITL approval |
| **Inputs** | Product description, competitive brief, 3 personas, user-defined launch timeline |
| **Capabilities** | Phased planning, channel recommendation, milestone generation, KPI definition |
| **Tools Used** | GTM framework library, channel performance benchmarks, calendar tool |
| **Outputs** | 3-phase launch plan (pre-launch, launch, post-launch) with milestones, channels, KPIs |
| **Memory** | Stores strategy in PostgreSQL; references for content and analytics agents |
| **HITL** | User adjusts timeline, phase duration, and channel priorities |
| **Eval Metrics** | Strategy completeness score, phase coherence, milestone specificity |
| **Latency Target** | < 60 seconds |
| **Error Handling** | Defaults to 4-week pre-launch + 1-week launch + 4-week post-launch if no timeline provided |

---

## 5. Content Generation Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Sonnet 4.6 |
| **Role** | Launch copywriter |
| **Trigger** | Dispatched after Launch Strategy HITL approval |
| **Inputs** | Product description, all 3 personas, approved strategy, brand voice (if provided) |
| **Capabilities** | Multi-format copy generation, persona-aware messaging, A/B variant creation |
| **Tools Used** | Brand voice analyzer, tone checker, A/B variant generator |
| **Outputs** | Per persona: email sequence (3 emails), 5 LinkedIn posts, 3 Twitter threads, 3 ad headlines |
| **Memory** | Stores approved copy in PostgreSQL; brand voice learned over time |
| **HITL** | User edits copy inline before finalizing |
| **Eval Metrics** | Copy relevance to persona, strategy alignment, readability score, user edit rate |
| **Latency Target** | < 120 seconds (large output volume) |
| **Error Handling** | Generate 1 content format if full suite times out; retry remainder in background |

---

## 6. Analytics & Feedback Agent

| Dimension | Detail |
|-----------|--------|
| **Model** | Claude Haiku 4.5 |
| **Role** | Performance monitor and optimizer |
| **Trigger** | Activated post-launch when user connects analytics tools |
| **Inputs** | GA4 events, email open/click rates, social engagement, HubSpot pipeline data |
| **Capabilities** | Metric aggregation, anomaly detection, optimization recommendation |
| **Tools Used** | GA4 MCP Server, HubSpot MCP Server, email platform API |
| **Outputs** | Performance summary (daily/weekly), top 3 optimization recommendations |
| **Memory** | Tracks metric history in PostgreSQL; learns what works per product category |
| **HITL** | User accepts or dismisses optimization recommendations |
| **Eval Metrics** | Recommendation acceptance rate, metric prediction accuracy, alert precision |
| **Latency Target** | < 30 seconds (summary generation) |
| **Error Handling** | Surface last known data with timestamp if live data unavailable |

---

## Agent Interaction Map

```
User Input
    │
    ▼
Orchestrator (Opus 4.6)
    │
    ├──► Market Intelligence Agent (Sonnet 4.6) ──► HITL ──┐
    │                                                       │
    ├──► Audience Insight Agent (Sonnet 4.6) ◄─────────────┤
    │         │                                             │
    │         └──► HITL ────────────────────────────────────┤
    │                                                       │
    ├──► Launch Strategy Agent (Opus 4.6) ◄─────────────────┤
    │         │                                             │
    │         └──► HITL ────────────────────────────────────┤
    │                                                       │
    ├──► Content Generation Agent (Sonnet 4.6) ◄────────────┤
    │         │                                             │
    │         └──► HITL ────────────────────────────────────┤
    │
    └──► Analytics & Feedback Agent (Haiku 4.5) [post-launch]
              │
              └──► HITL (recommendations)
```

---

## Capability Coverage Matrix

| Capability | Market Intel | Audience | Strategy | Content | Analytics |
|------------|:---:|:---:|:---:|:---:|:---:|
| Web research | ✓ | | | | |
| Competitor analysis | ✓ | | | | |
| Trend detection | ✓ | | | | |
| Persona building | | ✓ | | | |
| Segment mapping | | ✓ | | | |
| JTBD analysis | | ✓ | | | |
| GTM planning | | | ✓ | | |
| Channel selection | | | ✓ | | |
| Milestone generation | | | ✓ | | |
| Email copywriting | | | | ✓ | |
| Social copywriting | | | | ✓ | |
| Ad copy | | | | ✓ | |
| Performance tracking | | | | | ✓ |
| Optimization recs | | | | | ✓ |
| Anomaly detection | | | | | ✓ |
