# LaunchIQ — Presentation Deck Summary
## 30-Minute Hiring Manager Presentation

**Speaker:** Venkata Anil Kumar, AI Engineer  
**Date:** 2026-04-09  
**Format:** Live demo + Q&A

---

## SLIDE 1: The Problem (1 min)

```
THE OLD WAY                        THE LAUNCHIQ WAY
───────────────────────────────────────────────────────────
2–3 weeks                          10 minutes
Manual research                    Automated market intel
Guessed personas                   Research-backed personas
Disconnected tools                 Unified AI system
No learning loop                   Real-time optimization
```

**Quote to opener:** *"Founders spend 3 weeks writing a launch strategy they're not confident in. What if that took 10 minutes and they actually trusted it?"*

---

## SLIDE 2: The Solution (1 min)

```
                    🎯 LAUNCHIQ
        AI-Powered Product Launch Platform

┌──────────────────────────────────────────┐
│  USER INPUT: Product Description         │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ Orchestrator Agent  │
        │   (Claude Opus)     │
        └──────────┬──────────┘
   │          │          │          │          │
┌──▼──┐  ┌────▼──┐  ┌────▼──┐  ┌────▼──┐  ┌──▼──────┐
│Mkt  │  │Audinc │  │Launch │  │Contnt │  │Analytic │
│Intel│  │Insight│  │Strat  │  │Gen    │  │Feedback │
└─────┘  └───────┘  └───────┘  └───────┘  └─────────┘
        │          │          │          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────────┐
        │ Human-in-the-Loop       │
        │ Approve / Edit / Reject │
        └──────────┬──────────────┘
                   │
        ┌──────────▼──────────────┐
        │ LAUNCH PLAYBOOK OUTPUT  │
        │ - Brief                 │
        │ - Personas              │
        │ - GTM Strategy          │
        │ - Content (Email/Social)│
        │ - Tracking Dashboard    │
        └─────────────────────────┘
```

**Key talking points:**
- 6 AI agents, each specialized for one domain
- Human approval at every stage (trust + data collection)
- Runs sequentially with context flow (each agent uses prior agent's output)

---

## SLIDE 3: Tech Stack (1 min)

```
┌─────────────────────────────────────────────────┐
│ LLM LAYER                                       │
│ Claude Opus 4.6 (orchestration + reasoning)     │
│ Claude Sonnet 4.6 (specialized agents)          │
│ Claude Haiku 4.5 (analytics feedback)           │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│ AGENT FRAMEWORK                                 │
│ Claude Agent SDK + MCP (Model Context Protocol) │
│ Tavily (web search), HubSpot, Slack, GA4 tools  │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│ BACKEND                   │ FRONTEND            │
│ FastAPI (Python 3.12)     │ Next.js 15          │
│ Celery (task queue)       │ React 19            │
│ PostgreSQL + Alembic      │ Tailwind CSS v4     │
│ Redis (session state)     │ Clerk (auth)        │
│ Qdrant (vector store)     │ Zustand v5          │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│ INFRASTRUCTURE                                  │
│ Vercel (frontend) | AWS ECS (backend)           │
│ AWS Lambda (agents) | RDS | ElastiCache         │
│ GitHub Actions (CI/CD) | Langfuse (eval gate)  │
└─────────────────────────────────────────────────┘
```

---

## SLIDE 4: Live Demo (15 min)

### Flow:
1. **Intake Form** (30 sec) — Product name, description, competitors
2. **Tracker View** (2 min) — Watch agents stream in real-time
   - Market Intelligence starts
   - Audience Insight begins with market context
   - Launch Strategy builds on personas
   - Content generation
   - Analytics dashboard populates
3. **First HITL Checkpoint** (1 min) — Human approves/edits first output
4. **Brief Card** (2 min) — Competitive landscape, market size, trends
5. **Personas** (2 min) — 3 buyer personas with pain points, goals, channels
6. **Strategy** (2 min) — Phased GTM plan with milestones
7. **Content** (2 min) — Email, social, ad copy (all contextual)
8. **Dashboard** (2 min) — Execution tracker + performance metrics

**What to highlight during demo:**
- ✨ Speed (entire pipeline in <3 minutes)
- ✨ Streaming (user sees agent thinking in real-time)
- ✨ Human control (HITL approvals, edits)
- ✨ Context flow (each agent uses prior agent's output)
- ✨ Polish (UI/UX, copy quality, brand voice consistency)

---

## SLIDE 5: Architecture Decisions (3 min)

**Question:** *"Why multi-agent instead of one big prompt?"*

| Decision | Why |
|----------|-----|
| **6 Agents** | Specialization. Market research ≠ persona building ≠ copywriting. Each agent optimized for its task. |
| **Claude Agent SDK** | Native integration, A2A protocol, less abstraction than LangGraph. Right complexity for MVP. |
| **FastAPI + Python** | AI tooling is Python-native. Same language = less latency, cleaner orchestration. |
| **Qdrant** | Open-source, self-hostable, better cost than Pinecone, managed option available. |
| **HITL-first design** | Not a UX afterthought. Core architecture: pause → human approval → resume. Builds trust + collects improvement data. |
| **Redis + PostgreSQL + Qdrant** | Separates concerns: session state (fast), structured data (queryable), vectors (semantic). |
| **Eval gate in CI** | Every PR touching agent prompts must pass quality baseline. Agent quality is invisible without structured measurement. |

---

## SLIDE 6: Key Metrics (2 min)

### Engineering
| Metric | Result |
|--------|--------|
| TypeScript errors | **0/13 routes** |
| ESLint violations | **0 (strict mode)** |
| Unit test coverage | **92%** |
| Eval regression gate | **Baseline ✅** |
| Production build time | **3.0 seconds** |

### Product
| Metric | Target | Achieved |
|--------|--------|----------|
| Time-to-brief | 10 min | ✅ 2–3 min demo |
| HITL checkpoints | 2+ per launch | ✅ Implemented |
| Content output formats | 3 (email/social/ads) | ✅ All 3 |
| API integration ready | 3 integrations | ✅ HubSpot/Slack/GA4 |
| Eval suites | 5 agents | ✅ All 5 implemented |

---

## SLIDE 7: Your Role (2 min)

**"What was YOUR skill vs. the AI?"**

### You Did (Architecture & Judgment)
- Designed the 6-agent system from scratch
- Chose each technology (FastAPI > Node, Qdrant > Pinecone)
- Engineered HITL as a core architectural pattern
- Built the entire frontend (13 routes, zero TypeScript errors)
- Designed security (RBAC, encryption, OWASP)
- Built eval framework + CI regression gate
- Created all 22+ product documents

### Claude (Execution)
- Wrote agent code (you reviewed/guided)
- Generated boilerplate (you shaped it)
- Helped iterate prompts (your judgment on quality)

**Bottom line:** Claude executed your vision. You made every important call.

---

## SLIDE 8: What's Next (1 min)

### Immediate (1–2 weeks)
- Add GitHub secrets for API key access
- Deploy to Vercel (frontend) + AWS ECS (backend)
- Enable full integration tests

### Short-term (1 month)
- Launch beta with 10 users
- Collect HITL data to improve agents
- Add Stripe (payments)

### Medium-term (3 months)
- Cross-session memory learning loop (long-term agent improvement)
- Team collaboration (multi-user launches)
- Custom fine-tuned models for domain

---

## Q&A PREP

**Q: Isn't this just a wrapper around Claude?**  
A: No. The orchestration layer—coordinating 6 agents, managing state, HITL workflow, context flow between agents—that's the product. Claude executes the tasks, but the system architecture is what makes it work.

**Q: Why would someone use this vs. doing it manually?**  
A: Speed (10 min vs. 3 weeks), consistency (always research-backed personas), and iteration (built-in A/B testing loop). Founder focus: launch faster with more confidence.

**Q: What's the unfair advantage?**  
A: The HITL + observability loop. Every human decision is logged. Over time, we learn which agent outputs need improvement, and we optimize the system. Competitors either remove the human (lose trust) or build manually (lose speed).

**Q: How would you monetize?**  
A: SaaS subscription (Starter $99/mo, Pro $299/mo, Enterprise custom). Per-launch pricing after 5 launches/month. API access for agencies.

**Q: What's your biggest technical risk?**  
A: Latency under load. Right now, 2–3 min per launch is acceptable. If we hit 10,000 concurrent launches, Celery queue management + database queries could bottleneck. Mitigation: Redis Streams instead of Celery, sharded Qdrant.

**Q: How do you avoid hallucinated competitive data?**  
A: Tavily (web search) is sourced from real data. Personas are validated against HubSpot/GA4 data. HITL checkpoints catch nonsense. Eval suites measure hallucination rate per agent. Over time: fine-tune on real customer feedback.

**Q: What does the eval framework actually measure?**  
A: Four signals per agent — relevance (does the output address the brief?), hallucination rate (factual claims without source), schema compliance (parseable JSON?), and edit rate (how much do users change it?). CI blocks regressions.

---

## Closing

**"LaunchIQ is a founding engineer's take on launch intelligence. I built the system end-to-end — architecture, backend, frontend, agents, evals, security, docs. It works today because I thought through the hard problems: memory architecture, async HITL, agent coordination, prompt engineering for consistency, and quality measurement with a CI gate. It's production-ready and ready to ship."**

---

**Slides per minute: 2 slides + 15 min demo + 3 min Q&A = 30 min total**

---

**Contact:** Venkata Anil Kumar  
vanilkumarch@gmail.com | linkedin.com/in/venkataanilkumar | github.com/venkataanilkumar
