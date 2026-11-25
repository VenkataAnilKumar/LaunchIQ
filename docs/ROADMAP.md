# Status and roadmap

## Project Status

**Verified end to end (fake LLM, SQLite, local Redis, Celery or inline runner; 62 unit/API tests, browser E2E in Chromium):**
landing page → sample brief → create launch → live agent progress → formatted review checkpoint → read results mid-pause → approve / edit (form generated from the agent's schema) / reject → completed brief → document view and Markdown export → post-launch analytics from supplied metrics; dashboard search and filters; mobile layout; per-user isolation; failed-agent retry; cost budget.

**Not verified yet:** real Claude/Tavily runs (no live eval baseline recorded), PostgreSQL, Docker Compose, AWS CDK/Lambda/ECS and Vercel deploys, HubSpot/Slack integrations, Clerk in production.
**Not built:** GA4 connector, vector memory/RAG, billing, onboarding.


## Production Readiness (planned, not built)

Not everything below is needed for every use. What is required depends on the goal:

| Goal | Auth + security pass | Hosting | Billing + onboarding |
|------|----------------------|---------|----------------------|
| Private / portfolio demo (run locally) | not needed | not needed | not needed |
| Public demo anyone can try | **required** (real Clerk login, API in production mode) | **required** (one simple host) | skip |
| Charging customers | required | required | required |

Notes:
- The local dev login accepts unsigned tokens, so it must never be used on a public server.
- Every launch costs real model spend. A public demo also needs a per-user launch cap (the per-launch cost budget already exists).
- Error tracking (Sentry is wired in) is enough monitoring at first.

**Reuse instead of building from scratch** (all MIT; patterns to port, not templates to adopt, since none match FastAPI + Next.js + Clerk):
- Stripe Checkout, customer portal and subscription webhooks: [`nextjs/saas-starter`](https://github.com/nextjs/saas-starter) (about 330 lines of TypeScript to port to FastAPI; the `users` table already has a `plan` column).
- Docker Compose, Traefik with automatic HTTPS and deploy-on-merge CI: [`fastapi/full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template) (add Redis and the Celery worker, swap the Vite frontend for Next.js).
- Clerk token verification: replace the hand-written JWKS fetch in `src/apps/api/middleware/auth.py` with Clerk's official verification library.

Rough estimate: about 7-9 days with reuse versus 12-14 from scratch; the minimum for a public demo is about 3-4 days
(live eval baseline, Clerk login, per-user cap, one deploy).


## Roadmap

**Done**
- [x] Multi-agent pipeline with resumable human-review checkpoints (DB-backed, event-driven)
- [x] Real-time SSE dashboard (authenticated stream), status banner, retry, export
- [x] Offline eval gate in CI over a 16-brief corpus incl. prompt-injection briefs
- [x] Source grounding, prompt-injection guards, per-launch cost budget
- [x] Post-launch analytics from user-supplied metrics
- [x] Keyless local stack (`make local`)
- [x] A/B content variants by default; extended thinking on the strategy agent

**Next**
- [ ] Live eval baseline (needs `ANTHROPIC_API_KEY`) and real-model prompt tuning
- [ ] Billing, onboarding, production auth (Clerk) and security pass — see Production Readiness (only the parts your goal needs)
- [ ] Hosting, secrets and monitoring for production — see Production Readiness
- [ ] Vector memory (Qdrant) for reuse of past reports/personas, if it proves worth it
- [ ] GA4 connector for analytics

**Later**
- [ ] Slack bot — trigger and approve launches from Slack
- [ ] Brand voice learning — improve content from past launch performance
- [ ] Competitor monitoring — weekly automated market intelligence updates
- [ ] Multi-language content generation
- [ ] White-label API for marketing agencies

