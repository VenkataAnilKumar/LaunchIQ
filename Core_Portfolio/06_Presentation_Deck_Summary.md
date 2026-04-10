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
        │          │          │          │
   ┌────▼──┐  ┌────▼──┐  ┌────▼──┐  ┌────▼──┐
   │Market │  │Audience│ │Launch │  │Content│
   │Intel  │  │Insight │ │Strat  │  │Gen    │
   └───────┘  └───────┘  └───────┘  └───────┘
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
- Runs in parallel (fast) + sequentially (context-aware)

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
│ FastAPI (Python)          │ Next.js 15          │
│ Celery (task queue)       │ React 19            │
│ PostgreSQL (Supabase)     │ Tailwind CSS 4      │
│ Redis (session state)     │ Clerk (auth)        │
│ Qdrant (vector store)     │                     │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│ INFRASTRUCTURE                                  │
│ Vercel (frontend) | AWS ECS (backend)           │
│ RDS (database) | ElastiCache (redis)            │
│ GitHub Actions (CI/CD) | Langfuse (eval)       │
└─────────────────────────────────────────────────┘
```

---

## SLIDE 4: Live Demo (15 min)

### Flow:
1. **Intake Form** (30 sec) — Product name, description, competitors
2. **Tracker View** (2 min) — Watch agents stream in real-time
   - Market Intelligence starts
   - Audience Insight begins
   - Launch Strategy reasoning
   - Content generation
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

---

## SLIDE 6: Key Metrics (2 min)

### Engineering
| Metric | Result |
|--------|--------|
| TypeScript errors | **0/10 routes** |
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

---

## SLIDE 7: Your Role (2 min)

**"What was YOUR skill vs. the AI?"**

### You Did (Architecture & Judgment)
- Designed the 6-agent system from scratch
- Chose each technology (FastAPI > Node, Qdrant > Pinecone)
- Engineered HITL as a core pattern
- Built the entire frontend (13 routes, zero TypeScript errors)
- Designed security (RBAC, encryption, OWASP)
- Created all 16 product documents

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
- Add Stripe (payments) and PostHog (analytics)

### Medium-term (3 months)
- Custom fine-tuned models for domain
- Advanced competitor tracking
- Multi-user team collaboration

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
A: Tavily (web search) is sourced from real data. Personas are validated against HubSpot/GA4 data. HITL checkpoints catch nonsense. Over time: fine-tune on real customer feedback.

---

## Closing

**"LaunchIQ is a founding engineer's take on launch intelligence. I built the system end-to-end—architecture, backend, frontend, security, docs. It works today because I thought through the hard problems: memory architecture, async HITL, agent coordination, prompt engineering for consistency. And it's ready to ship."**

---

**Slides per minute: 2 slides + 15 min demo + 3 min Q&A = 30 min total**
