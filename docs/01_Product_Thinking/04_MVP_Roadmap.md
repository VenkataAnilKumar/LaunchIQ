# MVP Roadmap
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. MVP Goal

Deliver a working multi-agent launch intelligence platform that takes a product description as input and outputs a complete, actionable launch strategy — including market research, audience personas, competitive positioning, and ready-to-use campaign content — in under 10 minutes.

**MVP Success Criteria:**
- End-to-end launch brief generated in < 10 minutes
- All 5 core agents operational
- Human-in-the-Loop checkpoints at each major output
- At least 3 pilot users complete a full launch workflow
- NPS > 35 from pilot users

---

## 2. Roadmap Phases

### Phase 1 — NOW (Weeks 1–4): Core Intelligence Engine

| Feature | Description | Priority |
|---------|-------------|----------|
| Orchestrator Agent | Coordinates all sub-agents, manages workflow state | P0 |
| Market Intelligence Agent | Automated competitor & trend research | P0 |
| Audience Insight Agent | Generates buyer personas with messaging angles | P0 |
| Launch Strategy Generator | AI-generated phased GTM plan | P0 |
| Basic Web UI | Input form + results dashboard | P0 |
| HITL Checkpoints | Approve/edit at each agent output | P0 |
| Claude API Integration | Sonnet 4.6 for execution, Opus 4.6 for strategy | P0 |

**Phase 1 Exit Criteria:** User can input product → receive full launch brief with strategy

---

### Phase 2 — NEXT (Weeks 5–8): Content & Execution Layer

| Feature | Description | Priority |
|---------|-------------|----------|
| Content Generation Agent | Email sequences, social copy, ad headlines | P0 |
| Launch Checklist & Tracker | Step-by-step execution with status tracking | P0 |
| Competitive Positioning Map | Visual differentiation canvas | P1 |
| Launch Analytics Dashboard | Basic performance metrics view | P1 |
| PDF/Notion Export | Export launch brief and strategy | P1 |
| Short-term Agent Memory | Session context persistence | P1 |
| User Authentication | Clerk / Supabase auth | P0 |

**Phase 2 Exit Criteria:** User can go from brief → content → execution tracker in one session

---

### Phase 3 — LATER (Weeks 9–12): Intelligence & Integrations

| Feature | Description | Priority |
|---------|-------------|----------|
| Long-term Memory (Vector Store) | Persistent market knowledge per user | P1 |
| Analytics & Feedback Agent | Performance tracking + AI optimization tips | P1 |
| Slack Integration | Launch alerts and approvals in Slack | P2 |
| HubSpot Integration | Push contacts, sequences to HubSpot | P2 |
| GA4 Integration | Pull performance data for analytics agent | P2 |
| Multi-launch Management | Track and compare multiple launches | P2 |
| Team Collaboration (basic) | Share launch briefs with teammates | P3 |

**Phase 3 Exit Criteria:** Platform retains context across sessions, integrates with 2+ tools

---

## 3. Prioritization Rationale

| Principle | Application |
|-----------|-------------|
| Value first | Intelligence agents ship before integrations — core value must work standalone |
| Speed to wow | First launch brief < 10 min is the primary acquisition hook |
| HITL before autonomy | Trust is built incrementally — agent autonomy increases over time |
| Retention over acquisition | Integrations (Slack, HubSpot) are Phase 3 — retention drivers, not launch blockers |

---

## 4. What is NOT in MVP

- Native mobile app
- Real-time collaboration
- Custom model fine-tuning
- White-label version
- Physical product / e-commerce launches
- Non-English language support
- Direct ad platform integrations

---

## 5. Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Core agents working (P1) | Week 4 | Planned |
| End-to-end flow demo | Week 6 | Planned |
| Pilot user onboarding (3 users) | Week 8 | Planned |
| Content + tracker complete | Week 8 | Planned |
| Integrations (Slack, HubSpot) | Week 12 | Planned |
| Public beta launch | Week 14 | Planned |
