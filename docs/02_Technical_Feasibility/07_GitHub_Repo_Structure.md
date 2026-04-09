# GitHub Repository Structure
## LaunchIQ — AI-Powered Product Launch Intelligence Platform
### 2026 Monorepo Architecture

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. Repo Strategy

**Type:** Monorepo
**Manager:** pnpm workspaces (frontend) + Python workspace (backend/agents)
**Build System:** Turborepo (task caching, parallel execution)

**Why Monorepo:**
- Agents, tools, and memory share types — single source of truth
- One PR can span frontend + agent + eval changes atomically
- Shared CI/CD pipeline with per-package caching
- Independent deployability without independent repos

---

## 2. Top-Level Structure

```
launchiq/
│
├── README.md                        # GitHub landing page
├── turbo.json                       # Turborepo pipeline config
├── pnpm-workspace.yaml              # pnpm workspace definition
├── pyproject.toml                   # Python workspace root
├── docker-compose.yml               # Local dev services
├── .env.example                     # Environment variable template
├── .gitignore
├── .editorconfig
│
├── docs/                            # All product documentation
│   ├── 01_Product_Thinking/
│   ├── 02_Technical_Feasibility/
│   └── 03_AI_Architecture/
│
├── src/                             # All source code
│   ├── apps/                        # Deployable applications
│   ├── agents/                      # AI agent modules
│   ├── packages/                    # Shared code
│   ├── tools/                       # MCP server implementations
│   ├── memory/                      # Memory layer modules
│   ├── evals/                       # Evaluation framework
│   └── infra/                       # Infrastructure as code
│
└── .github/                         # CI/CD + GitHub config
    ├── workflows/
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 3. docs/ — Product Documentation

```
docs/
├── 01_Product_Thinking/
│   ├── 01_PRD.md
│   ├── 02_User_Research_Summary.md
│   ├── 03_Competitive_Analysis.md
│   ├── 04_MVP_Roadmap.md
│   ├── 05_GTM_Strategy.md
│   ├── 06_Business_Model_Canvas.md
│   ├── 07_Product_Document.md
│   └── 08_Onboarding_Flow.md
│
├── 02_Technical_Feasibility/
│   ├── 01_Technical_Architecture.md
│   ├── 02_GitHub_README.md
│   ├── 03_Demo_Video_Script.md
│   ├── 04_Tech_Stack_Decisions.md
│   ├── 05_Security_Compliance.md
│   ├── 06_End_to_End_Product_Architecture.md
│   └── 07_GitHub_Repo_Structure.md    ← this document
│
└── 03_AI_Architecture/
    ├── 01_Agent_Capability_Matrix.md
    ├── 02_Data_Flow_Diagram.md
    ├── 03_Agentic_AI_References_2026.md
    └── 04_Agentic_AI_Architecture.md
```

---

## 4. src/apps/ — Deployable Applications

```
src/apps/
│
├── web/                             # Next.js 15 Frontend
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/
│   │   │   │   └── page.tsx
│   │   │   └── sign-up/
│   │   │       └── page.tsx
│   │   ├── (app)/
│   │   │   ├── layout.tsx           # App shell + sidebar
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx         # All launches overview
│   │   │   ├── launch/
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx     # Product intake form
│   │   │   │   └── [id]/
│   │   │   │       ├── layout.tsx   # Launch tabs layout
│   │   │   │       ├── brief/
│   │   │   │       │   └── page.tsx # Market Intelligence output
│   │   │   │       ├── personas/
│   │   │   │       │   └── page.tsx # Audience Insight output
│   │   │   │       ├── strategy/
│   │   │   │       │   └── page.tsx # Launch Strategy output
│   │   │   │       ├── content/
│   │   │   │       │   └── page.tsx # Content Generation output
│   │   │   │       └── tracker/
│   │   │   │           └── page.tsx # Execution tracker
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   └── api/
│   │       └── [...proxy]/
│   │           └── route.ts         # Thin proxy to FastAPI
│   ├── components/
│   │   ├── agents/
│   │   │   ├── AgentPipeline.tsx    # Live agent progress view
│   │   │   ├── AgentCard.tsx        # Individual agent status card
│   │   │   └── AgentStream.tsx      # SSE streaming output
│   │   ├── hitl/
│   │   │   ├── HITLCheckpoint.tsx   # Approve/Edit/Regenerate UI
│   │   │   ├── HITLDecisionBar.tsx  # Action bar at checkpoint
│   │   │   └── HITLEditModal.tsx    # Inline edit before approve
│   │   ├── launch/
│   │   │   ├── IntakeForm.tsx       # Product description input
│   │   │   ├── BriefCard.tsx        # Competitor card component
│   │   │   ├── PersonaCard.tsx      # Persona display component
│   │   │   ├── StrategyPhase.tsx    # GTM phase component
│   │   │   └── ContentBlock.tsx     # Copy block component
│   │   └── ui/                      # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts                   # FastAPI client
│   │   ├── sse.ts                   # SSE hook (useAgentStream)
│   │   ├── ws.ts                    # WebSocket hook (useHITL)
│   │   └── utils.ts
│   ├── store/
│   │   ├── launchStore.ts           # Zustand — launch state
│   │   └── agentStore.ts            # Zustand — agent run state
│   ├── public/
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── tsconfig.json
│
└── api/                             # FastAPI Backend
    ├── main.py                      # FastAPI app entrypoint
    ├── routers/
    │   ├── launches.py              # Launch CRUD
    │   ├── agents.py                # Agent run + stream endpoints
    │   ├── hitl.py                  # HITL decision endpoints
    │   ├── integrations.py          # HubSpot, Slack, GA4 connect
    │   └── health.py                # Health + metrics
    ├── middleware/
    │   ├── auth.py                  # Clerk JWT validation
    │   ├── rate_limit.py            # Per-user rate limiting
    │   ├── pii_scrubber.py          # Strip PII from inputs
    │   └── security_headers.py      # HSTS, CSP, X-Frame
    ├── services/
    │   ├── launch_service.py        # Launch business logic
    │   ├── agent_service.py         # Agent dispatch + monitoring
    │   ├── stream_service.py        # SSE + WebSocket management
    │   └── hitl_service.py          # HITL state management
    ├── models/
    │   ├── launch.py                # Pydantic + SQLAlchemy models
    │   ├── agent.py
    │   ├── user.py
    │   └── hitl.py
    ├── workers/
    │   ├── celery_app.py            # Celery configuration
    │   └── tasks.py                 # Agent task definitions
    ├── config.py                    # Settings (pydantic-settings)
    ├── requirements.txt
    └── Dockerfile
```

---

## 5. src/agents/ — Agent Modules

Each agent is an **independently deployable unit** with its own Lambda handler, system prompt, tool config, and tests.

```
src/agents/
│
├── _base/                           # Shared agent foundation
│   ├── base_agent.py                # Base class all agents inherit
│   ├── cognitive_loop.py            # Perceive→Reason→Act→Validate→Reflect
│   ├── context_builder.py           # Builds compressed context per agent
│   └── output_validator.py          # Pydantic schema validation
│
├── orchestrator/
│   ├── agent.py                     # Orchestrator agent definition
│   ├── workflow_state.py            # Redis workflow state machine
│   ├── dispatcher.py                # Sub-agent dispatch via A2A
│   ├── synthesizer.py               # Final playbook synthesis
│   ├── prompts/
│   │   └── system.md                # Orchestrator system prompt
│   ├── handler.py                   # AWS Lambda handler
│   └── tests/
│       ├── test_agent.py
│       └── test_workflow.py
│
├── market_intelligence/
│   ├── agent.py                     # Market Intelligence agent
│   ├── researcher.py                # Research orchestration logic
│   ├── competitor_analyzer.py       # Competitor card builder
│   ├── trend_detector.py            # Trend signal extractor
│   ├── prompts/
│   │   ├── system.md                # System prompt
│   │   ├── research.md              # Research task prompt
│   │   └── analyze.md               # Analysis prompt
│   ├── schemas.py                   # Output schema (Pydantic)
│   ├── handler.py                   # AWS Lambda handler
│   └── tests/
│       ├── test_agent.py
│       ├── test_researcher.py
│       └── fixtures/
│           └── sample_brief.json
│
├── audience_insight/
│   ├── agent.py
│   ├── persona_builder.py           # JTBD persona synthesis
│   ├── segment_mapper.py            # Market segment analysis
│   ├── messaging_generator.py       # Per-persona messaging angles
│   ├── prompts/
│   │   ├── system.md
│   │   └── persona.md
│   ├── schemas.py
│   ├── handler.py
│   └── tests/
│
├── launch_strategy/
│   ├── agent.py
│   ├── phase_builder.py             # Pre/launch/post-launch phases
│   ├── channel_selector.py          # Channel recommendation
│   ├── milestone_generator.py       # Milestone + KPI definition
│   ├── prompts/
│   │   ├── system.md
│   │   └── strategy.md
│   ├── schemas.py
│   ├── handler.py
│   └── tests/
│
├── content_generation/
│   ├── agent.py
│   ├── email_writer.py              # Email sequence generator
│   ├── social_writer.py             # LinkedIn + Twitter copy
│   ├── ad_writer.py                 # Google + Meta ad headlines
│   ├── brand_voice.py               # Brand voice adapter
│   ├── prompts/
│   │   ├── system.md
│   │   ├── email.md
│   │   ├── social.md
│   │   └── ads.md
│   ├── schemas.py
│   ├── handler.py
│   └── tests/
│
└── analytics_feedback/
    ├── agent.py
    ├── metrics_aggregator.py        # Pull + normalize metrics
    ├── anomaly_detector.py          # KPI deviation detection
    ├── recommendation_engine.py     # Optimization suggestions
    ├── prompts/
    │   ├── system.md
    │   └── recommend.md
    ├── schemas.py
    ├── handler.py
    └── tests/
```

---

## 6. src/packages/ — Shared Code

```
src/packages/
│
├── types/                           # Shared TypeScript types
│   ├── launch.ts
│   ├── agent.ts
│   ├── hitl.ts
│   └── index.ts
│
├── config/                          # Shared configuration
│   ├── constants.py                 # Python constants
│   ├── constants.ts                 # TypeScript constants
│   └── models.py                    # Model name constants
│
└── utils/
    ├── logger.py                    # Structured JSON logger
    ├── retry.py                     # Retry decorator with backoff
    ├── token_counter.py             # Token budget tracking
    └── context_compressor.py        # Compress context for handoff
```

---

## 7. src/tools/ — MCP Server Implementations

Each MCP server is a **standalone service** exposing tools via MCP protocol.

```
src/tools/
│
├── _base/
│   ├── base_mcp_server.py           # Base MCP server class
│   └── tool_registry.py             # Tool manifest + auth scope
│
├── tavily_search/
│   ├── server.py                    # MCP server
│   ├── tools.py                     # web_search, news_search tools
│   ├── schemas.py                   # Input/output schemas
│   └── tests/
│
├── hubspot/
│   ├── server.py
│   ├── tools.py                     # contacts, deals, sequences
│   ├── auth.py                      # OAuth flow
│   ├── schemas.py
│   └── tests/
│
├── slack/
│   ├── server.py
│   ├── tools.py                     # send_message, get_channel
│   ├── auth.py
│   ├── schemas.py
│   └── tests/
│
├── ga4/
│   ├── server.py
│   ├── tools.py                     # get_events, get_goals
│   ├── auth.py
│   ├── schemas.py
│   └── tests/
│
└── internal/
    ├── server.py
    ├── tools.py                     # persona_templates, gtm_frameworks
    ├── schemas.py
    └── tests/
```

---

## 8. src/memory/ — Memory Layer

```
src/memory/
│
├── short_term/                      # Redis — session memory
│   ├── session_store.py             # Workflow state per launch
│   ├── scratchpad.py                # Agent scratchpad per run
│   ├── hitl_state.py                # HITL pause/resume state
│   └── tests/
│
├── long_term/                       # Qdrant — vector memory
│   ├── qdrant_client.py             # Qdrant connection + config
│   ├── market_store.py              # Market intel embeddings
│   ├── persona_store.py             # Persona vector store
│   ├── brand_voice_store.py         # Brand voice embeddings
│   ├── embeddings.py                # text-embedding-3 wrapper
│   └── tests/
│
└── structured/                      # PostgreSQL — relational memory
    ├── database.py                  # SQLAlchemy engine + session
    ├── migrations/                  # Alembic migration files
    │   └── versions/
    ├── repositories/
    │   ├── launch_repo.py
    │   ├── brief_repo.py
    │   ├── persona_repo.py
    │   ├── strategy_repo.py
    │   ├── content_repo.py
    │   └── hitl_repo.py
    └── tests/
```

---

## 9. src/evals/ — Evaluation Framework

```
src/evals/
│
├── framework/
│   ├── evaluator.py                 # Base evaluator class
│   ├── langfuse_client.py           # Langfuse integration
│   ├── scorer.py                    # Quality score computation
│   └── reporter.py                  # Eval report generation
│
├── suites/
│   ├── market_intelligence/
│   │   ├── eval_suite.py            # Full eval suite
│   │   ├── test_cases.json          # Golden test inputs
│   │   └── expected_outputs.json    # Expected output patterns
│   ├── audience_insight/
│   │   ├── eval_suite.py
│   │   ├── test_cases.json
│   │   └── expected_outputs.json
│   ├── launch_strategy/
│   │   ├── eval_suite.py
│   │   ├── test_cases.json
│   │   └── expected_outputs.json
│   ├── content_generation/
│   │   ├── eval_suite.py
│   │   ├── test_cases.json
│   │   └── expected_outputs.json
│   └── end_to_end/
│       ├── e2e_eval.py              # Full pipeline eval
│       └── test_cases.json
│
├── metrics/
│   ├── relevance.py                 # Output relevance scoring
│   ├── hallucination.py             # Hallucination detection
│   ├── schema_compliance.py         # Schema validation rate
│   └── edit_rate.py                 # HITL edit rate tracking
│
├── regression/
│   ├── baseline.json                # Approved baseline scores
│   ├── run_regression.py            # Compare against baseline
│   └── update_baseline.py           # Update baseline on approval
│
└── reports/
    └── .gitkeep                     # Eval reports (gitignored)
```

---

## 10. src/infra/ — Infrastructure as Code

```
src/infra/
│
├── aws/                             # AWS CDK (Python)
│   ├── app.py                       # CDK app entrypoint
│   ├── stacks/
│   │   ├── agents_stack.py          # Lambda functions per agent
│   │   ├── api_stack.py             # ECS Fargate + ALB
│   │   ├── data_stack.py            # RDS, ElastiCache, S3
│   │   └── secrets_stack.py         # Secrets Manager
│   ├── constructs/
│   │   ├── agent_lambda.py          # Reusable agent Lambda construct
│   │   └── mcp_server.py            # Reusable MCP server construct
│   └── requirements.txt
│
├── vercel/
│   └── vercel.json                  # Vercel project config
│
└── docker/
    ├── api.Dockerfile               # FastAPI production image
    ├── worker.Dockerfile            # Celery worker image
    └── mcp.Dockerfile               # MCP server image
```

---

## 11. .github/ — CI/CD Pipelines

```
.github/
│
├── workflows/
│   │
│   ├── pr.yml                       # Pull Request checks
│   │   # Triggers: PR opened / updated
│   │   # Steps:
│   │   #   1. Lint (ruff, eslint)
│   │   #   2. Type check (mypy, tsc)
│   │   #   3. Unit tests (pytest, vitest)
│   │   #   4. Eval gate (agent quality must pass)
│   │   #   5. Preview deploy (Vercel)
│   │
│   ├── deploy-staging.yml           # Deploy to staging
│   │   # Triggers: push to dev branch
│   │   # Steps:
│   │   #   1. Run full test suite
│   │   #   2. Run regression evals
│   │   #   3. Build + push Docker images
│   │   #   4. Deploy API to ECS (staging)
│   │   #   5. Deploy agents to Lambda (staging)
│   │   #   6. Deploy frontend to Vercel (staging)
│   │   #   7. Smoke tests
│   │
│   ├── deploy-production.yml        # Deploy to production
│   │   # Triggers: semver tag (v1.x.x)
│   │   # Steps:
│   │   #   1. All staging steps +
│   │   #   2. Blue/green Lambda deployment
│   │   #   3. ECS rolling update
│   │   #   4. Post-deploy health checks
│   │   #   5. Notify Slack on success/failure
│   │
│   └── eval-scheduled.yml           # Scheduled eval runs
│       # Triggers: every Monday 09:00 UTC
│       # Steps:
│       #   1. Run full eval suite against production
│       #   2. Compare against baseline
│       #   3. Post report to Slack
│       #   4. Alert if any metric regresses > 10%
│
└── PULL_REQUEST_TEMPLATE.md
    # PR template with:
    # - What changed
    # - Agent(s) affected
    # - Eval results (paste scores)
    # - HITL impact (does this change HITL behavior?)
    # - Test evidence
```

---

## 12. Branch Strategy

```
main          → production (protected, requires PR + eval gate)
dev           → staging (auto-deploy on push)
│
├── feature/* → new features (frontend, API)
├── agent/*   → agent changes (prompts, logic, tools)
├── eval/*    → eval improvements (new test cases, metrics)
├── infra/*   → infrastructure changes
└── hotfix/*  → production hotfixes (merge to main + dev)
```

**Branch protection rules (main):**
- Require PR with 1 approval (solo: self-review)
- Require eval gate to pass
- Require all status checks to pass
- No direct pushes

---

## 13. Environment Management

```
.env.example                         # Template (committed)
.env.local                           # Local dev (gitignored)
.env.staging                         # Staging (gitignored)
.env.production                      # Production (gitignored)

Environment variables by layer:
─────────────────────────────────
# Core AI
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL_OPUS=claude-opus-4-6
ANTHROPIC_MODEL_SONNET=claude-sonnet-4-6
ANTHROPIC_MODEL_HAIKU=claude-haiku-4-5-20251001

# Database
SUPABASE_URL=
SUPABASE_KEY=
DATABASE_URL=

# Vector Store
QDRANT_URL=
QDRANT_API_KEY=

# Cache + Queue
REDIS_URL=

# Auth
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=

# MCP Tools
TAVILY_API_KEY=
HUBSPOT_API_KEY=
SLACK_BOT_TOKEN=
GA4_PROPERTY_ID=

# Observability
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=launchiq-prod
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
SENTRY_DSN=
NEXT_PUBLIC_POSTHOG_KEY=

# Infrastructure
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=
```

---

## 14. Local Development Setup

```bash
# 1. Clone
git clone https://github.com/username/launchiq.git
cd launchiq

# 2. Install dependencies
pnpm install                         # Frontend + shared packages
pip install -r src/apps/api/requirements.txt

# 3. Start local services
docker-compose up -d
# Starts: PostgreSQL, Redis, Qdrant

# 4. Run database migrations
cd src/memory/structured
alembic upgrade head

# 5. Start development servers
pnpm dev                             # Next.js on :3000
uvicorn src.apps.api.main:app --reload  # FastAPI on :8000
celery -A src.apps.api.workers.celery_app worker  # Celery worker

# 6. Run evals (verify agent quality)
python src/evals/suites/end_to_end/e2e_eval.py
```

---

## 15. Complete Repo at a Glance

```
launchiq/
├── README.md
├── turbo.json
├── pnpm-workspace.yaml
├── pyproject.toml
├── docker-compose.yml
├── .env.example
│
├── docs/                            # 20 product documents
│   ├── 01_Product_Thinking/         # 8 docs
│   ├── 02_Technical_Feasibility/    # 7 docs
│   └── 03_AI_Architecture/          # 4 docs (+ references)
│
├── src/
│   ├── apps/
│   │   ├── web/                     # Next.js 15 frontend
│   │   └── api/                     # FastAPI backend + Celery
│   │
│   ├── agents/                      # 6 agent modules
│   │   ├── _base/
│   │   ├── orchestrator/
│   │   ├── market_intelligence/
│   │   ├── audience_insight/
│   │   ├── launch_strategy/
│   │   ├── content_generation/
│   │   └── analytics_feedback/
│   │
│   ├── packages/                    # Shared types, config, utils
│   │   ├── types/
│   │   ├── config/
│   │   └── utils/
│   │
│   ├── tools/                       # MCP server implementations
│   │   ├── _base/
│   │   ├── tavily_search/
│   │   ├── hubspot/
│   │   ├── slack/
│   │   ├── ga4/
│   │   └── internal/
│   │
│   ├── memory/                      # Memory layer
│   │   ├── short_term/              # Redis
│   │   ├── long_term/               # Qdrant
│   │   └── structured/              # PostgreSQL
│   │
│   ├── evals/                       # Evaluation framework
│   │   ├── framework/
│   │   ├── suites/
│   │   ├── metrics/
│   │   └── regression/
│   │
│   └── infra/                       # Infrastructure as code
│       ├── aws/                     # AWS CDK
│       ├── vercel/
│       └── docker/
│
└── .github/
    ├── workflows/
    │   ├── pr.yml
    │   ├── deploy-staging.yml
    │   ├── deploy-production.yml
    │   └── eval-scheduled.yml
    └── PULL_REQUEST_TEMPLATE.md
```

---

*This structure is designed to grow. Add agents by adding a folder in `src/agents/`. Add tools by adding a folder in `src/tools/`. Every addition follows the same pattern.*
