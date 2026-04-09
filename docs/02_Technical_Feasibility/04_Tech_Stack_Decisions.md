# Tech Stack Decisions
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## Decision Log Format

Each decision includes: **What** was chosen, **Why** over alternatives, and **Trade-offs** accepted.

---

## 1. LLM Provider — Anthropic Claude

**Chosen:** Claude Opus 4.6 (orchestration/strategy) + Sonnet 4.6 (execution) + Haiku 4.5 (speed tasks)

**Why over alternatives:**
- Claude's extended context window handles large market research documents without chunking failures
- Claude Agent SDK provides native multi-agent orchestration — no wrapper needed
- Strongest reasoning quality for strategy generation vs. GPT-4o at comparable cost
- MCP (Model Context Protocol) native support for tool integration
- Superior instruction-following for structured agent output

**Trade-offs:**
- Single provider dependency (mitigated by abstraction layer)
- Slightly higher cost per token vs. GPT-4o mini for simple tasks (offset by Haiku for speed tasks)

---

## 2. Agent Framework — Claude Agent SDK

**Chosen:** Claude Agent SDK (Anthropic native)

**Why over alternatives:**
- LangGraph: More flexible but complex to configure; overkill for MVP agent topology
- CrewAI: Good for simple crews, limited for complex memory + tool orchestration
- AutoGen: Microsoft-centric, heavier dependency footprint
- Claude Agent SDK is native to our LLM provider — tighter integration, less abstraction overhead

**Trade-offs:**
- Less community tooling vs. LangChain ecosystem
- Tied to Anthropic SDK versioning

---

## 3. Backend Framework — FastAPI (Python 3.12)

**Chosen:** FastAPI

**Why over alternatives:**
- Node.js/Express: Python is dominant in AI/ML tooling; avoids language-switching in agent code
- Django: Too heavy for an API-first service; REST + async is all we need
- FastAPI is async-native, auto-generates OpenAPI docs, and has excellent Pydantic integration for structured agent outputs

**Trade-offs:**
- Python GIL limits true parallelism (mitigated by async + Celery workers)
- Smaller ecosystem than Node.js for some frontend-adjacent tools

---

## 4. Frontend Framework — Next.js 15 + React 19

**Chosen:** Next.js 15 with App Router + React 19

**Why over alternatives:**
- Remix: Smaller ecosystem, less deployment flexibility
- Vite + React SPA: No SSR, worse SEO and initial load for marketing pages
- Next.js 15 Server Components reduce client bundle size for AI output rendering
- React 19 concurrent features improve streaming agent output UX

**Trade-offs:**
- App Router has steeper learning curve vs. Pages Router
- More complexity than a pure SPA for MVP — accepted for long-term scalability

---

## 5. Database — PostgreSQL via Supabase

**Chosen:** Supabase (PostgreSQL + Auth + Realtime + Storage)

**Why over alternatives:**
- Firebase: NoSQL is wrong for structured launch/strategy data with relational queries
- PlanetScale: MySQL-based, less powerful for JSON + vector-adjacent queries
- Raw RDS: More ops overhead for a solo founder
- Supabase gives managed PostgreSQL + Row Level Security + built-in auth + edge functions in one platform

**Trade-offs:**
- Supabase vendor lock-in (mitigated — underlying PostgreSQL is portable)
- Free tier limits require upgrade at scale

---

## 6. Vector Database — Qdrant

**Chosen:** Qdrant

**Why over alternatives:**
- Pinecone: Managed, but expensive at scale and limited query flexibility
- Weaviate: More complex to operate, heavier resource footprint
- pgvector: Good for simple use cases, but not optimized for large-scale semantic search
- Qdrant is open-source, self-hostable, fast, and has excellent Python SDK

**Trade-offs:**
- Self-hosting adds ops overhead (mitigated by Qdrant Cloud managed option)
- Smaller community vs. Pinecone

---

## 7. Cache & Task Queue — Redis

**Chosen:** Redis (session cache) + Celery (task queue)

**Why over alternatives:**
- Memcached: Less feature-rich, no pub/sub for real-time agent status
- SQS/RabbitMQ: More complex setup for MVP; Celery + Redis is well-understood
- Redis handles both caching and message brokering in one service

**Trade-offs:**
- Redis memory cost scales with data volume
- Celery adds worker process management complexity

---

## 8. Auth — Clerk

**Chosen:** Clerk

**Why over alternatives:**
- Auth0: More expensive, more complex for solo founder setup
- Supabase Auth: Functional but less polished UI components
- NextAuth: Good for simple OAuth, but custom flows require more work
- Clerk provides pre-built React components, excellent DX, magic links, and social OAuth out of the box

**Trade-offs:**
- Clerk vendor dependency for auth flows
- Cost increases at scale (acceptable for MVP and early growth)

---

## 9. Observability — LangSmith + Langfuse + Sentry

**Chosen:** LangSmith (agent tracing) + Langfuse (evals) + Sentry (errors)

**Why over alternatives:**
- Datadog: Expensive, not AI-native
- Helicone: Good for LLM cost tracking, but less agent-aware than LangSmith
- LangSmith is purpose-built for tracing agent workflows and tool calls
- Langfuse is open-source and excellent for eval pipelines and A/B testing prompts

**Trade-offs:**
- Multiple observability tools adds integration overhead
- LangSmith cost scales with trace volume

---

## 10. Infrastructure — Vercel + AWS Lambda

**Chosen:** Vercel (frontend) + AWS Lambda (agent workers)

**Why over alternatives:**
- Full AWS: More ops complexity, slower to iterate for solo founder
- Fly.io: Good alternative, less mature for Python workloads
- Vercel gives zero-config Next.js deployment with edge CDN
- AWS Lambda scales to zero, keeping costs minimal during early adoption

**Trade-offs:**
- Lambda cold starts can impact agent response time (mitigated by provisioned concurrency for critical paths)
- Split infrastructure requires coordination between two platforms

---

## Summary Table

| Layer | Choice | Key Reason |
|-------|--------|-----------|
| LLM | Claude Opus/Sonnet/Haiku | Native agent SDK + best reasoning |
| Agent Framework | Claude Agent SDK | Native integration, MCP support |
| Backend | FastAPI Python 3.12 | AI-native, async, clean APIs |
| Frontend | Next.js 15 + React 19 | SSR, streaming, modern DX |
| Database | Supabase PostgreSQL | Managed, RLS, auth included |
| Vector DB | Qdrant | Open-source, fast, self-hostable |
| Cache/Queue | Redis + Celery | Session memory + async tasks |
| Auth | Clerk | Best DX for rapid auth setup |
| Observability | LangSmith + Langfuse + Sentry | Full agent + eval + error coverage |
| Infrastructure | Vercel + AWS Lambda | Zero-config + scale-to-zero |
