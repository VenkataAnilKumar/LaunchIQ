# LaunchIQ

AI-powered launch orchestration platform that helps teams go from product idea to execution-ready launch plan using coordinated multi-agent workflows.

## Product Overview

LaunchIQ turns a product brief into a complete launch package:

- Market and competitor intelligence
- Audience personas and messaging angles
- Phased go-to-market strategy
- Channel-ready launch content (email, social, ads)
- Feedback loop recommendations from analytics signals

The platform is built with human-in-the-loop checkpoints so users approve strategic outputs before the pipeline advances.

## Why LaunchIQ

Most teams run launches across disconnected docs, spreadsheets, and tools. LaunchIQ consolidates the workflow into one system with domain agents orchestrated by a central coordinator.

Key outcomes:

- Faster planning: minutes instead of weeks
- Better consistency: structured outputs across all launch phases
- Better control: approval gates at critical decision points
- Better reuse: persistent memory and reusable launch assets

## Core Agent System

LaunchIQ uses a multi-agent architecture:

1. Orchestrator Agent: controls workflow, retries, state, and HITL checkpoints
2. Market Intelligence Agent: research, trend signals, competitor analysis
3. Audience Insight Agent: persona generation and segment messaging
4. Launch Strategy Agent: phased plan, channels, milestones, risks
5. Content Generation Agent: campaign-ready copy from strategy context
6. Analytics Feedback Agent: performance insights and optimization suggestions

## Current Build Status

Implemented:

- FastAPI backend with middleware for auth, rate limiting, and security headers
- Orchestrator + worker agent modules
- Celery task workers for async orchestration and per-agent execution
- MCP-style tool servers for Tavily, HubSpot, Slack, GA4, and internal tools
- Structured memory repositories and short-term session/HITL state management
- Product and architecture documentation under docs/

In progress:

- Full frontend product experience in src/apps/web (currently scaffold-level)

## Repository Structure

```text
LaunchIQ/
  docs/
    01_Product_Thinking/
    02_Technical_Feasibility/
    03_AI_Architecture/
  src/
    agents/
      _base/
      orchestrator/
      market_intelligence/
      audience_insight/
      launch_strategy/
      content_generation/
      analytics_feedback/
    apps/
      api/
      web/
    memory/
      short_term/
      long_term/
      structured/
    tools/
      _base/
      tavily_search/
      internal/
      hubspot/
      slack/
      ga4/
  docker-compose.yml
  pyproject.toml
```

## Tech Stack

- Backend: Python 3.12, FastAPI, Celery, SQLAlchemy
- AI: Anthropic models (Opus, Sonnet, Haiku)
- Data: PostgreSQL, Redis, Qdrant
- Integrations: Tavily, HubSpot, Slack, GA4
- Frontend: Next.js (scaffold in repo)

## Local Development

### Prerequisites

- Python 3.12+
- Poetry
- Docker + Docker Compose

### 1. Install dependencies

```bash
poetry install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Update required keys in .env, especially:

- ANTHROPIC_API_KEY
- DATABASE_URL
- REDIS_URL
- CLERK_SECRET_KEY
- TAVILY_API_KEY

### 3. Start local infrastructure

```bash
docker-compose up -d
```

Starts:

- PostgreSQL on 5432
- Redis on 6379
- Qdrant on 6333

### 4. Run API

```bash
poetry run uvicorn src.apps.api.main:app --reload
```

API docs:

- http://localhost:8000/docs (disabled in production mode)

### 5. Run worker

```bash
poetry run celery -A src.apps.api.workers.celery_app.celery_app worker --loglevel=info
```

## Testing and Quality

```bash
poetry run pytest
poetry run ruff check src
poetry run mypy src
```

## Product Documentation

Detailed product docs are in docs/:

- Product thinking and roadmap: docs/01_Product_Thinking
- Technical architecture and implementation: docs/02_Technical_Feasibility
- Agent architecture and data flow: docs/03_AI_Architecture

## Roadmap

Near-term priorities:

- Complete production-ready frontend flows for launch lifecycle
- Add deeper integration actions (publish, sync, campaign operations)
- Expand analytics feedback to closed-loop performance optimization
- Add richer team collaboration and launch workspace controls

## License

MIT
