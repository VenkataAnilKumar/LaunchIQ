<div align="center">

<img src="docs/assets/launchiq-logo.svg" alt="LaunchIQ" width="90" height="90" />

# LaunchIQ

**Turn a product brief into a researched, human-reviewed launch plan.**

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![CI](https://img.shields.io/github/actions/workflow/status/venkataanilkumar/launchiq/pr.yml?style=flat-square&label=CI&logo=githubactions&logoColor=white)](https://github.com/venkataanilkumar/launchiq/actions)

[Demo](docs/demo/README.md) · [Architecture](docs/ARCHITECTURE.md) · [Reference](docs/REFERENCE.md) · [Roadmap](docs/ROADMAP.md)

<img src="docs/demo/screenshots/04-review-market.webp" alt="LaunchIQ review step: formatted market research with Approve, Edit and Reject (demo data)" width="100%"/>

</div>

## What it does

You describe a product: name, description, target market and, optionally, competitors. Four AI agents then work in order,
and **you review the results at two checkpoints** before the pipeline continues.

| Step | Agent | Output |
|------|-------|--------|
| 1 | Market Intelligence | Competitors, trends (with sources), white space, positioning |
| | **Review: approve, edit or reject** | |
| 2 | Audience Insight | Personas and messaging framework |
| 3 | Launch Strategy | Phased launch plan, channels, budget, risks |
| | **Review: approve, edit or reject** | |
| 4 | Content Generation | Email, social and ad copy, each in A/B variants |

You get one launch document (rendered in the app, downloadable as Markdown) and, after launch, recommendations based on the
metrics you measure.

## Quick start (no API keys, no Docker)

Runs the whole product against an offline **fake model**, so the generated text is placeholder content. It shows the flow,
not real model quality. Needs Python 3.12+, Node 22+, pnpm and `redis-server`.

```bash
pip install -r src/apps/api/requirements.txt
make local                                  # API on :8000 (fake model, SQLite, local Redis)
cd src/apps/web && pnpm install
NEXT_PUBLIC_DEV_BEARER_TOKEN=$(python3 ../../../scripts/dev_token.py) pnpm dev     # http://localhost:3000
```

For real output, set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` (plus `SEARCH_PROVIDER=tavily` and `TAVILY_API_KEY` for
web search). A guided 6-minute walkthrough with exact inputs is in [`docs/demo/`](docs/demo/README.md); the Docker route,
the HTTP API and all settings are in [`docs/REFERENCE.md`](docs/REFERENCE.md).

## Tech stack

| Layer | Technology |
|-------|-----------|
| Agents | Anthropic Claude (Opus, Sonnet and Haiku tiers), tool-use loop, offline fake model |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2 (async), Celery, Alembic |
| Data | PostgreSQL (SQLite for local runs), Redis |
| Frontend | Next.js 15, React 19, TanStack Query, Zustand, Clerk |
| Quality | pytest, ruff, ESLint and tsc, Playwright, an offline eval gate, GitHub Actions |

Full stack, versions and design decisions: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Repository layout

```
src/agents/      orchestrator and the five agents
src/apps/api/    FastAPI backend          src/apps/web/   Next.js frontend
src/tools/       tool executors (Tavily is wired in)
src/memory/      Redis and SQL layers     src/evals/      brief corpus and eval gate
src/infra/       AWS CDK and Dockerfiles (designed, not deployed)
docs/            product, architecture and demo docs      scripts/   local stack and browser tests
```

## Status

**Verified:** the full flow on the fake model (create, live progress, two reviews with editing, results, export, analytics),
about 70 automated tests, an offline eval gate and Chromium end-to-end tests.
**Not verified yet:** runs with the real Claude and Tavily APIs (so real quality, run time and cost are unmeasured),
PostgreSQL, the Docker route, and any cloud deployment. **Not built:** billing, hosted sign-in setup, the GA4 connector.
Details and next steps: [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Documentation

[Demo walkthrough](docs/demo/README.md) · [Architecture](docs/ARCHITECTURE.md) · [Reference (API, settings, evals)](docs/REFERENCE.md) ·
[Roadmap](docs/ROADMAP.md) · [Deployment notes](docs/DEPLOYMENT.md) · [Product docs](docs/01_Product_Thinking/01_PRD.md) ·
[Hiring managers and investors](docs/portfolio/09_Hiring_Managers_and_Investors.md)

## License

[MIT](LICENSE) · Made by Venkata Anil Kumar
