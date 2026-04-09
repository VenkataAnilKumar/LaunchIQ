# LaunchIQ — GitHub Copilot Prompts (Phase-wise)

> Copy each prompt into **Copilot Chat** (sidebar) or **Copilot Edits** (multi-file mode).
> Always open the target file(s) in your editor before sending — Copilot uses open tabs as context.
> Complete phases in order.

---

## How to Use

| Mode | When to use |
|------|-------------|
| **Copilot Chat** (`Ctrl+Alt+I`) | Single-file implementations, questions, debugging |
| **Copilot Edits** (`Ctrl+Shift+I`) | Multi-file changes across a phase |
| **Inline** (`Ctrl+I`) | Fill in a specific function body |

**Before every prompt:**
1. Open the file(s) you want Copilot to write in the editor
2. Open `docs/02_Technical_Feasibility/08_Implementation_Plan.md` in a tab
3. Paste the prompt below into Copilot Chat

---

## MASTER CONTEXT PROMPT
> Paste this **once at the start of every Copilot Chat session**. Sets the project context so you don't need to repeat it.

```
You are implementing LaunchIQ — an AI-powered product launch intelligence platform.

ARCHITECTURE:
- 6 AI agents (Python, AWS Lambda): orchestrator, market_intelligence, audience_insight, launch_strategy, content_generation, analytics_feedback
- FastAPI backend (ECS Fargate) at src/apps/api/
- Next.js 15 frontend (Vercel) at src/apps/web/
- Memory: Redis (short-term), Qdrant (long-term/vectors), PostgreSQL (structured)
- MCP tool servers: Tavily search, HubSpot, Slack, GA4, Internal
- Eval framework with Langfuse integration and CI regression gate

MODEL ASSIGNMENTS (never change these):
- orchestrator: claude-opus-4-6
- market_intelligence: claude-sonnet-4-6
- audience_insight: claude-sonnet-4-6
- launch_strategy: claude-opus-4-6 (with extended thinking enabled)
- content_generation: claude-sonnet-4-6
- analytics_feedback: claude-haiku-4-5-20251001

TECH STACK:
- Python 3.12, FastAPI, SQLAlchemy (async), Alembic, Celery, Redis, Qdrant
- anthropic SDK (latest), pydantic v2, pydantic-settings
- Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Zustand, React Query
- Auth: Clerk (JWT)
- Monorepo: Turborepo + pnpm workspaces

CODING RULES:
- All Python: use `from __future__ import annotations`, type hints everywhere, async/await
- All agent outputs must be validated against Pydantic schemas (OutputValidator)
- Never hardcode API keys — always use settings from config.py
- Each agent file must be independently importable (no circular imports)
- Lambda handlers must be synchronous wrappers around async agent code
- Follow the exact file structure in src/ — do not create new folders

The full implementation plan is in: docs/02_Technical_Feasibility/08_Implementation_Plan.md
Already implemented: src/agents/_base/ (all 4 files), src/apps/api/main.py, src/apps/api/config.py, src/apps/api/routers/ (health, launches, agents, hitl)
```

---

## PHASE 1 — Foundation & Data Layer

### Prompt 1A — Shared Types (TypeScript)

> Open: `src/packages/types/launch.ts`, `src/packages/types/agent.ts`, `src/packages/types/hitl.ts`, `src/packages/types/index.ts`

```
Implement all 4 TypeScript type files in src/packages/types/.

launch.ts — define these interfaces:
- Launch: { launch_id, status (union: 'pending'|'running'|'hitl_pending'|'completed'|'failed'), product_name, description, target_market, competitors: string[], launch_date?, created_at, updated_at }
- LaunchBrief: { launch_id, market_data?, personas?, strategy?, content? }
- MarketData, Persona, LaunchStrategy, ContentBundle as placeholder interfaces with key fields

agent.ts — define:
- AgentStatus type union: 'pending'|'running'|'completed'|'failed'|'skipped'
- AgentId type union of all 6 agent names
- AgentRun interface: { agent_id: AgentId, launch_id, status: AgentStatus, output?, tokens_used?, started_at?, completed_at?, error? }

hitl.ts — define:
- HITLDecision type: 'approve'|'edit'|'reject'
- HITLCheckpoint type: 'brief_review'|'persona_review'|'strategy_review'|'content_review'
- HITLState interface: { launch_id, checkpoint: HITLCheckpoint, agent_id: AgentId, output_preview: Record<string,unknown>, decision?, edits?, created_at, resolved_at? }

index.ts — re-export everything from the 3 files above.

Use only TypeScript types/interfaces — no classes, no runtime code.
```

---

### Prompt 1B — Python Config (`src/packages/config/`)

> Open: `src/packages/config/models.py`, `src/packages/config/constants.py`, `src/packages/config/constants.ts`

```
Implement 3 config files:

src/packages/config/models.py:
- AGENT_MODELS dict: maps each agent_id to its model string (see model assignments in context)
- HITL_CHECKPOINTS list: ['brief_review', 'persona_review', 'strategy_review', 'content_review']
- PIPELINE_SEQUENCE list: the 4 worker agents in order (market_intelligence → content_generation)

src/packages/config/constants.py:
- MAX_CONTEXT_TOKENS = 180000
- MAX_OUTPUT_TOKENS = 8192
- HITL_TIMEOUT_SECONDS = 86400
- CELERY_TASK_TIMEOUT = 300
- RATE_LIMIT_REQUESTS = 60
- RATE_LIMIT_WINDOW = 60

src/packages/config/constants.ts:
- Same constants as Python file but TypeScript exports
- Add: API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
- Add: SSE_RECONNECT_DELAY_MS = 3000

All Python files use from __future__ import annotations.
```

---

### Prompt 1C — Python Utils (`src/packages/utils/`)

> Open: `src/packages/utils/logger.py`, `src/packages/utils/retry.py`, `src/packages/utils/token_counter.py`, `src/packages/utils/context_compressor.py`

```
Implement 4 utility files in src/packages/utils/:

logger.py:
- get_logger(name: str) -> logging.Logger
- Structured format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
- Writes to stdout
- No duplicate handlers (check before adding)

retry.py:
- with_retry(max_attempts=3, delay=1.0, backoff=2.0) decorator
- Works on async functions only
- Exponential backoff between attempts
- Re-raises on final attempt

token_counter.py:
- estimate_tokens(text: str) -> int — uses 4 chars ≈ 1 token heuristic
- estimate_messages_tokens(messages: list[dict]) -> int — handles string and list content blocks
- is_within_budget(messages: list[dict], budget: int = 180000) -> bool

context_compressor.py:
- truncate_to_budget(text: str, max_tokens: int) -> str — truncates text to fit token budget
- compress_messages(messages: list[dict], max_tokens: int) -> list[dict] — removes oldest messages first to fit budget, always keeps the last user message

All files: from __future__ import annotations, full type hints.
```

---

### Prompt 1D — SQLAlchemy Models (`src/apps/api/models/`)

> Open: `src/apps/api/models/launch.py`, `src/apps/api/models/agent.py`, `src/apps/api/models/hitl.py`, `src/apps/api/models/user.py`

```
Implement all 4 SQLAlchemy models using SQLAlchemy 2.x async style.

IMPORTANT: Define Base = DeclarativeBase() only in launch.py. All other models import Base from .launch.

launch.py:
- LaunchStatus(str, Enum): PENDING, RUNNING, HITL_PENDING, COMPLETED, FAILED
- Launch(Base): launch_id (String PK), user_id (String, indexed), status, product_name, description (Text), target_market, competitors (JSON), launch_date (nullable), brief_output (JSON nullable), created_at, updated_at

agent.py:
- AgentRun(Base): id (Integer PK autoincrement), launch_id (String, indexed), agent_id (String), status (String, default 'pending'), output (JSON nullable), tokens_used (Integer default 0), error (Text nullable), started_at (DateTime nullable), completed_at (DateTime nullable)

hitl.py:
- HITLCheckpointRecord(Base): id (String PK), launch_id (String, indexed), checkpoint, agent_id, output_preview (JSON), decision (String nullable), edits (JSON nullable), comment (Text nullable), created_at, resolved_at (nullable)

user.py:
- User(Base): user_id (String PK — Clerk user ID), email (String, unique), plan (String default 'free'), integrations (JSON default dict), created_at

All DateTime columns: default=datetime.utcnow. Use Column-based mapping (not mapped_column).
```

---

### Prompt 1E — Database + Repositories

> Open: `src/memory/structured/database.py` and all 6 files in `src/memory/structured/repositories/`

```
Implement database.py and all 6 repository files.

database.py (src/memory/structured/database.py):
- create_async_engine with NullPool (Lambda-safe)
- async_sessionmaker that yields AsyncSession
- get_db() async generator for FastAPI Depends injection
- engine URL from get_settings().database_url

launch_repo.py — LaunchRepository:
- create(user_id, data) -> Launch: creates with uuid4 launch_id
- get(launch_id) -> Launch | None
- list_by_user(user_id) -> list[Launch]
- update_status(launch_id, status) -> None
- save_brief_output(launch_id, output: dict) -> None

agent_repo.py — AgentRepository:
- create(launch_id, agent_id) -> AgentRun
- get_by_launch(launch_id) -> list[AgentRun]: returns all agents for a launch
- update_status(launch_id, agent_id, status, output=None, error=None) -> None
- set_started(launch_id, agent_id) -> None: sets status=running + started_at=utcnow
- set_completed(launch_id, agent_id, output, tokens_used) -> None
- reset_agent(launch_id, agent_id) -> bool: resets to pending for retry

hitl_repo.py — HITLRepository:
- create(launch_id, checkpoint, agent_id, output_preview) -> HITLCheckpointRecord: uuid4 id
- resolve(launch_id, decision, edits, comment) -> None: sets decision + resolved_at

brief_repo.py, persona_repo.py, strategy_repo.py, content_repo.py:
- Each wraps JSON read/write to the Launch.brief_output JSONB field for their section
- get(launch_id) -> dict | None
- save(launch_id, data: dict) -> None

All repositories take AsyncSession in __init__. All methods are async. Use SQLAlchemy select/update.
```

---

### Prompt 1F — Redis + Qdrant Clients

> Open: `src/memory/short_term/session_store.py`, `src/memory/short_term/hitl_state.py`, `src/memory/short_term/scratchpad.py`, `src/memory/long_term/qdrant_client.py`, `src/memory/long_term/embeddings.py`

```
Implement Redis and Qdrant client files.

session_store.py:
- get_redis() -> aioredis.Redis: singleton from settings.redis_url
- SessionStore class:
  - set(launch_id, key, value: dict, ttl=3600) -> None: key pattern "session:{launch_id}:{key}"
  - get(launch_id, key) -> dict | None
  - delete(launch_id, key) -> None
  - publish(channel: str, event: dict) -> None: Redis pub/sub publish, JSON-encodes event

hitl_state.py:
- HITLStateStore class:
  - set_pending(launch_id, state: dict) -> None: key "hitl:{launch_id}", TTL 24h
  - get_pending(launch_id) -> dict | None
  - resolve(launch_id, decision, edits) -> None: updates existing record with decision+edits
  - clear(launch_id) -> None: deletes key

scratchpad.py:
- AgentScratchpad class: temporary key-value store per agent run
  - write(launch_id, agent_id, key, value) -> None: key "scratch:{launch_id}:{agent_id}:{key}", TTL 1h
  - read(launch_id, agent_id, key) -> str | None
  - clear_all(launch_id, agent_id) -> None: deletes all keys matching pattern

qdrant_client.py:
- get_qdrant() -> AsyncQdrantClient: singleton
- COLLECTION_MARKET_DATA = "market_data", COLLECTION_PERSONAS = "personas", COLLECTION_BRAND_VOICE = "brand_voice"
- VECTOR_SIZE = 1536
- ensure_collections() -> None: creates collections if they don't exist (Distance.COSINE)
- upsert(collection, id, vector, payload) -> None
- search(collection, vector, limit=5) -> list[dict]: returns payload dicts of top matches

embeddings.py:
- embed_text(text: str) -> list[float]: calls OpenAI text-embedding-3-small (1536 dims) via openai SDK
- embed_batch(texts: list[str]) -> list[list[float]]
- Use settings.openai_api_key (add this field to Settings in config.py with default "")

Use redis.asyncio for Redis. Use qdrant_client AsyncQdrantClient. from __future__ import annotations everywhere.
```

---

## PHASE 2 — API Core

### Prompt 2A — Middleware (all 4 files)

> Open all 4 middleware files in `src/apps/api/middleware/`

```
Implement all 4 FastAPI middleware files. All extend BaseHTTPMiddleware from starlette.

security_headers.py — SecurityHeadersMiddleware:
- Add headers to every response: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block, Strict-Transport-Security: max-age=31536000; includeSubDomains
- Skip adding CSP header (handled by Next.js)

pii_scrubber.py — PIIScrubberMiddleware:
- Define scrub(text: str) -> str function that replaces:
  - Email addresses → [EMAIL]
  - Phone numbers (US format) → [PHONE]
  - Credit card numbers (13-16 digits) → [CARD]
  - SSN patterns → [SSN]
- Middleware: for POST/PUT requests with JSON content-type, read body, scrub it, replace request body
- Re-attach scrubbed body to request so downstream handlers receive clean data

rate_limit.py — RateLimitMiddleware:
- Skip paths starting with /api/v1/health and /docs
- Use Redis key "rate:{client_ip}" with 60s window, 60 request limit
- Return 429 with Retry-After header when exceeded
- Use redis pipeline for atomic INCR + EXPIRE

auth.py — ClerkAuthMiddleware:
- Skip: /api/v1/health, /api/v1/health/ready, /docs, /openapi.json
- Extract Bearer token from Authorization header, return 401 if missing
- In development (not is_production): decode JWT without verification, set request.state.user_id = payload["sub"]
- In production: raise NotImplementedError with message "Wire up Clerk JWKS verification"
- Return 401 with {"error": "invalid_token"} on any JWT decode error
```

---

### Prompt 2B — Services (all 4 files)

> Open all files in `src/apps/api/services/`

```
Implement 4 service files. These are the business logic layer between routers and the data/agent layers.

launch_service.py — LaunchService:
- create(data: dict, user_id: str = "dev") -> dict: creates Launch + pre-creates AgentRun records for all 4 pipeline agents, returns {launch_id, status, created_at}
- get(launch_id: str) -> dict | None: returns full launch detail including pipeline agent statuses
- run_pipeline(launch_id: str) -> None: calls run_orchestrator_task.delay(launch_id) from workers/tasks.py
- get_launch_service() factory function at module level

agent_service.py — AgentService:
- get_pipeline_status(launch_id) -> list[dict] | None: reads AgentRun records, returns list of status dicts
- retry(launch_id, agent_id) -> bool: resets agent to pending, calls run_single_agent_task.delay
- get_agent_service() factory function

stream_service.py — StreamService:
- sse_generator(launch_id) -> AsyncIterator[str]: subscribes to Redis channel "launch:{launch_id}:events", yields SSE-formatted strings ("data: {json}\n\n"), sends initial "connected" event, unsubscribes on generator close
- get_stream_service() factory function

hitl_service.py — HITLService:
- get_pending(launch_id) -> dict | None: reads from HITLStateStore
- resolve(launch_id, decision, edits, comment) -> dict | None: updates HITLStateStore, publishes "hitl_resolved" event to Redis pub/sub channel "launch:{launch_id}:hitl", clears pending state, returns {next_step}
- get_hitl_service() factory function

All services use AsyncSessionLocal for DB access. All async. Import types from models using TYPE_CHECKING guard to avoid circular imports.
```

---

### Prompt 2C — Integrations Router + __init__ files

> Open: `src/apps/api/routers/integrations.py`

```
Implement src/apps/api/routers/integrations.py.

Routes:
- GET /integrations — list connected integrations for current user {hubspot: bool, slack: bool, ga4: bool}
- POST /integrations/hubspot — store HubSpot OAuth credentials for user
- DELETE /integrations/hubspot — disconnect HubSpot
- POST /integrations/slack — store Slack bot token for user  
- DELETE /integrations/slack — disconnect Slack
- POST /integrations/ga4 — store GA4 property ID + credentials
- DELETE /integrations/ga4 — disconnect GA4

All POST bodies: {credentials: dict} (generic — specific validation in Phase 5).
All routes require auth (user_id from request.state.user_id).
Store integration data in User.integrations JSON column via UserRepository.
Return {"status": "connected"} on success, {"status": "disconnected"} on delete.

Also create UserRepository in src/memory/structured/repositories/ (if not existing):
- get(user_id) -> User | None
- create_or_update(user_id, email, data) -> User
- update_integrations(user_id, integration_name, credentials) -> None
- remove_integration(user_id, integration_name) -> None
```

---

## PHASE 3 — Orchestrator Agent

### Prompt 3A — Orchestrator (all files)

> Open ALL files in `src/agents/orchestrator/`, plus `src/agents/_base/base_agent.py` for reference

```
Implement the full Orchestrator agent. Read src/agents/_base/base_agent.py first to understand the base class.

workflow_state.py — WorkflowState dataclass:
- Fields: launch_id, brief: dict, agent_outputs: dict (default empty), current_agent: str|None, hitl_pending: bool, hitl_checkpoint: str|None, completed_agents: list[str], failed: bool, failure_reason: str|None
- Methods: mark_agent_complete(agent_id, output), mark_hitl_pending(checkpoint), resume_from_hitl(edits: dict|None) — merges edits into last agent's output if provided

dispatcher.py — AgentDispatcher:
- AGENT_MODULE_MAP: dict mapping agent_id strings to module paths
- dispatch(agent_id, payload) -> dict: imports agent module dynamically, instantiates agent class, calls .run(payload), returns result.output
- Helper _to_class_name(agent_id) -> str: "market_intelligence" → "MarketIntelligenceAgent"

schemas.py — OrchestratorOutput(BaseModel):
- launch_id: str
- status: str ("completed" | "failed" | "hitl_pending")
- agent_outputs: dict[str, Any]
- hitl_checkpoint: str | None

prompts/system.md — system prompt explaining orchestrator role, pipeline order, HITL checkpoints (after market_intelligence → "brief_review", after launch_strategy → "strategy_review"), validation rules.

agent.py — OrchestratorAgent(BaseAgent):
- Model: claude-opus-4-6, enable_thinking=True, thinking_budget=8000
- PIPELINE_SEQUENCE = ["market_intelligence", "audience_insight", "launch_strategy", "content_generation"]
- HITL_AFTER = {"market_intelligence": "brief_review", "launch_strategy": "strategy_review"}
- run(payload) -> AgentResult:
  1. Create WorkflowState
  2. For each agent in PIPELINE_SEQUENCE:
     - Publish "agent_started" event to Redis
     - Build payload with prior_outputs from state.agent_outputs
     - Call dispatcher.dispatch(agent_id, agent_payload)
     - On success: mark complete, publish "agent_completed" event
     - On failure: retry once, then mark failed and break
     - If agent_id in HITL_AFTER: call _pause_for_hitl(), await _wait_for_hitl_resolution() — if rejected: break
  3. Return AgentResult with OrchestratorOutput
- _pause_for_hitl(state, checkpoint, output): stores in HITLStateStore + publishes "hitl_required" event
- _wait_for_hitl_resolution(launch_id, timeout=86400): polls HITLStateStore every 2s until decision found or timeout
- _publish_event(launch_id, event): publishes to SessionStore
- stream() just calls run() and yields JSON

handler.py — Lambda handler:
- handler(event, context) -> dict: extracts payload, calls asyncio.run(agent.run(payload)), returns {statusCode: 200, body: json result}

tests/test_agent.py: 
- test that run() calls dispatcher for each pipeline agent
- test HITL pause/resume flow
- mock all external calls (Redis, dispatcher)
```

---

### Prompt 3B — Celery Workers

> Open: `src/apps/api/workers/celery_app.py`, `src/apps/api/workers/tasks.py`

```
Implement Celery app and tasks.

celery_app.py:
- Create Celery app named "launchiq"
- broker and backend both from settings.redis_url
- include: ["src.apps.api.workers.tasks"]
- Configure: task_serializer="json", result_serializer="json", accept_content=["json"], task_acks_late=True, worker_prefetch_multiplier=1, task_soft_time_limit=280, task_time_limit=300

tasks.py:
- run_orchestrator_task(launch_id: str): 
  1. Update launch status to RUNNING in DB
  2. Instantiate OrchestratorAgent
  3. Load brief from DB using _load_brief(launch_id)
  4. asyncio.run(agent.run(payload))
  5. Update launch status to COMPLETED or FAILED based on result
  6. On exception: update status to FAILED, publish error event to Redis

- run_single_agent_task(launch_id: str, agent_id: str):
  1. Update agent status to RUNNING in DB
  2. Load brief + prior outputs
  3. asyncio.run(dispatcher.dispatch(agent_id, payload))
  4. Update agent status to COMPLETED with output

- _load_brief(launch_id) -> dict: async helper that loads Launch from DB and returns brief dict

Both tasks: bind=True, max_retries=1, autoretry_for=(Exception,), retry_backoff=True
```

---

## PHASE 4 — Worker Agents

### Prompt 4A — Market Intelligence Agent

> Open: all files in `src/agents/market_intelligence/`, plus `src/agents/_base/base_agent.py` for reference

```
Implement the complete Market Intelligence agent.

schemas.py:
- Competitor(BaseModel): name, positioning, strengths: list[str], weaknesses: list[str], pricing: str|None
- MarketTrend(BaseModel): trend, relevance, source: str|None
- MarketIntelligenceOutput(BaseModel): market_size, growth_rate, competitors: list[Competitor] (1-10), trends: list[MarketTrend] (1-10), white_space, recommended_positioning

prompts/system.md: Write a focused system prompt. The agent must:
1. Use tavily_search tool to research market, competitors, trends (minimum 3 searches)
2. Return structured JSON matching MarketIntelligenceOutput schema exactly
3. Never fabricate statistics — only use search results
4. Always cite source for market size claims

prompts/research.md: Sub-prompt for the research phase — guide the agent to search for: "[product] market size 2026", "[competitor] pricing positioning", "[market] trends 2026"

prompts/analyze.md: Sub-prompt for analysis phase — guide extraction of white space and positioning recommendation

researcher.py — MarketResearcher class:
- build_search_queries(brief: dict) -> list[str]: generates 4-6 targeted search queries from the brief
- extract_competitor_data(search_results: list[dict]) -> list[dict]

trend_detector.py — TrendDetector:
- extract_trends(search_results: list[dict]) -> list[dict]: parses trends from search results

competitor_analyzer.py — CompetitorAnalyzer:
- analyze(search_results: list[dict], known_competitors: list[str]) -> list[dict]

agent.py — MarketIntelligenceAgent(BaseAgent):
- Model: claude-sonnet-4-6, tools=[TAVILY_TOOL], max_tokens=4096
- TAVILY_TOOL definition with input_schema
- run(payload) -> AgentResult:
  1. Build user message from payload (product_name, description, target_market, competitors)
  2. Call _call_with_tools(messages, TavilySearchExecutor())
  3. Extract JSON from response using _extract_json(text) helper
  4. Validate with _validate_output(output_dict)
  5. Return AgentResult
- stream(): yield JSON of result
- _extract_json(text) -> dict: regex to extract ```json blocks or raw {...}

handler.py: Lambda handler wrapping agent.run()

tests/test_agent.py: Mock anthropic.Anthropic and TavilySearchExecutor. Test that output matches MarketIntelligenceOutput schema.

tests/fixtures/sample_brief.json: realistic JSON for a SaaS product launch brief.
```

---

### Prompt 4B — Audience Insight Agent

> Open: all files in `src/agents/audience_insight/`, plus `src/agents/market_intelligence/agent.py` as reference pattern

```
Implement the complete Audience Insight agent. No external tool calls — uses prior market intelligence output as context.

schemas.py:
- Persona(BaseModel): name, role, age_range, pain_points: list[str] (2-5), goals: list[str] (2-5), channels: list[str], message_hook (≤15 words), willingness_to_pay
- AudienceInsightOutput(BaseModel): primary_persona: Persona, secondary_personas: list[Persona] (0-3), icp_summary, messaging_framework: dict[str,str], recommended_channels: list[str]

prompts/system.md: Agent must build personas from market data in context, not generic templates. Each persona must reference specific pain points from the market research. Return JSON matching AudienceInsightOutput.

prompts/persona.md: Detailed persona construction guide — include demographics, psychographics, buying behavior, channel preferences.

persona_builder.py — PersonaBuilder:
- build_primary(market_data: dict) -> dict: extracts ICP signal from market data
- build_secondary(market_data: dict, primary: dict) -> list[dict]

segment_mapper.py — SegmentMapper:
- map_segments(personas: list[dict]) -> dict[str, str]: persona name → core message

messaging_generator.py — MessagingGenerator:
- generate_hooks(personas: list[dict]) -> dict[str, str]

agent.py — AudienceInsightAgent(BaseAgent):
- Model: claude-sonnet-4-6, NO tools
- run(payload) -> AgentResult:
  1. Extract prior_outputs["market_intelligence"] from payload
  2. Build context dict with market_data
  3. Build messages using _build_messages(user_msg, context={"market_data": market_data})
  4. Call client.messages.create() directly (no tools)
  5. Extract + validate JSON output
  6. Return AgentResult

handler.py + tests/ following same pattern as market_intelligence.
```

---

### Prompt 4C — Launch Strategy Agent

> Open: all files in `src/agents/launch_strategy/`

```
Implement the Launch Strategy agent. Uses extended thinking (claude-opus-4-6).

schemas.py:
- LaunchPhase(BaseModel): phase ("Pre-Launch"|"Launch Week"|"Post-Launch"|"Growth"), duration, goals: list[str], tactics: list[str] (min 3), kpis: list[str]
- LaunchStrategyOutput(BaseModel): positioning_statement, launch_date_recommendation, phases: list[LaunchPhase] (3-4), channels: list[str], budget_allocation: dict[str,str], success_metrics: list[str], risks: list[str]

prompts/system.md: This agent creates launch plans. It has access to market data AND personas. Must produce actionable 90-day launch plan. Return JSON matching LaunchStrategyOutput.

prompts/strategy.md: Detailed strategy construction guide — positioning, phase breakdown, channel selection based on personas, risk identification.

phase_builder.py — PhaseBuilder: build_phases(market_data, personas) -> list[dict]
channel_selector.py — ChannelSelector: select_channels(personas, budget) -> list[str]
milestone_generator.py — MilestoneGenerator: generate_milestones(phases) -> list[dict]

agent.py — LaunchStrategyAgent(BaseAgent):
- Model: claude-opus-4-6, enable_thinking=True, thinking_budget=10000, NO tools
- Context includes: market_data from market_intelligence output, personas from audience_insight output
- run() follows same pattern as AudienceInsightAgent but with larger context
- Return AgentResult with thinking text preserved

handler.py + tests/ with schema validation test.
```

---

### Prompt 4D — Content Generation Agent

> Open: all files in `src/agents/content_generation/`

```
Implement the Content Generation agent. Uses parallelization for 3 content types.

schemas.py:
- ContentItem(BaseModel): format ("email"|"linkedin"|"twitter"|"ad_copy"|"landing_page"), variant ("a"|"b"), headline, body, cta, target_persona
- ContentBundle(BaseModel): email_sequence: list[ContentItem] (3-5), social_posts: list[ContentItem] (3-10), ad_copy: list[ContentItem] (2-4), brand_voice_notes: str

prompts/system.md: Content writer that matches brand voice and targets specific personas. Every piece must reference the strategy's positioning statement. Return JSON matching ContentBundle.

prompts/email.md: Email sequence guide — awareness email, consideration email, conversion email, nurture email. Subject lines ≤50 chars.

prompts/social.md: Social content guide — LinkedIn (thought leadership), Twitter/X (conversational), each with A/B variants.

prompts/ads.md: Ad copy guide — headline ≤30 chars, body ≤90 chars, strong CTA. Google + Meta formats.

brand_voice.py — BrandVoiceExtractor:
- extract(strategy_output: dict) -> dict: extracts tone, vocabulary, key messages from strategy

email_writer.py, social_writer.py, ad_writer.py: Each is a thin wrapper that calls the agent with the specific sub-prompt.

agent.py — ContentGenerationAgent(BaseAgent):
- Model: claude-sonnet-4-6
- run(payload) -> AgentResult:
  1. Extract strategy + personas from prior_outputs
  2. Generate all 3 content types IN PARALLEL using asyncio.gather():
     - _generate_email_sequence(strategy, personas)
     - _generate_social_posts(strategy, personas)
     - _generate_ad_copy(strategy, personas)
  3. Each _generate_* method makes a separate client.messages.create() call with its specific sub-prompt
  4. Merge results into ContentBundle
  5. Validate + return AgentResult
- Each _generate_* method uses max_tokens=2048

handler.py + tests/.
```

---

### Prompt 4E — Analytics & Feedback Agent

> Open: all files in `src/agents/analytics_feedback/`

```
Implement the Analytics & Feedback agent. Uses GA4 tool + Haiku model (cost-optimized).

schemas.py:
- Recommendation(BaseModel): area, insight, action, priority ("high"|"medium"|"low")
- AnalyticsOutput(BaseModel): engagement_score: float (0-1), top_performing_content: list[str], underperforming_content: list[str], recommendations: list[Recommendation] (min 3), predicted_next_action: str

GA4_TOOL definition:
{
  "name": "ga4_get_metrics",
  "description": "Fetch Google Analytics 4 metrics for a property",
  "input_schema": {
    "type": "object",
    "properties": {
      "property_id": {"type": "string"},
      "metrics": {"type": "array", "items": {"type": "string"}},
      "dimensions": {"type": "array", "items": {"type": "string"}},
      "date_range": {"type": "object", "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}}
    },
    "required": ["property_id", "metrics"]
  }
}

prompts/system.md: Analyzes launch performance data. If GA4 data available, use it. If not, analyze content bundle to predict performance. Return JSON matching AnalyticsOutput.

metrics_aggregator.py — MetricsAggregator: aggregate(ga4_data: dict) -> dict
anomaly_detector.py — AnomalyDetector: detect(metrics: dict) -> list[str]
recommendation_engine.py — RecommendationEngine: generate(metrics: dict, content: dict) -> list[dict]

agent.py — AnalyticsFeedbackAgent(BaseAgent):
- Model: claude-haiku-4-5-20251001 (cost optimization), tools=[GA4_TOOL]
- run(payload): if ga4_property_id in payload, call with tools; otherwise call without tools
- handler.py + tests/
```

---

## PHASE 5 — MCP Tool Servers

### Prompt 5A — Tavily Search Server

> Open: all files in `src/tools/tavily_search/` and `src/tools/_base/`

```
Implement the Tavily search MCP tool server.

src/tools/_base/base_mcp_server.py:
- BaseMCPServer abstract class with execute(tool_name: str, inputs: dict) -> dict abstract method
- Input validation gate: validate inputs against a schema before executing

src/tools/_base/tool_registry.py:
- ToolRegistry class: register(name, executor, schema), get(name), list_all() -> list[str]
- Global REGISTRY singleton

src/tools/tavily_search/schemas.py:
- TavilySearchInput(BaseModel): query: str (min 3 chars), max_results: int = 5 (1-10), search_depth: str = "advanced"
- TavilySearchResult(BaseModel): results: list[dict], answer: str|None, query: str

src/tools/tavily_search/tools.py — TavilySearchExecutor:
- Inherits BaseMCPServer
- execute(tool_name, inputs) -> dict: validates with TavilySearchInput, calls Tavily API
- _search(query, max_results, search_depth) -> dict: POST to https://api.tavily.com/search with api_key from settings
- Add tavily_api_key: str = "" to Settings in config.py
- Handles httpx.HTTPStatusError: returns {"error": "search_failed", "detail": str(e)}

src/tools/tavily_search/server.py:
- FastMCP server definition (if using fastmcp library) OR simple class that exposes tools list
- Tool: "tavily_search" with description and input_schema

Write a test in a tests/ folder: mock httpx.AsyncClient, verify query is passed correctly.
```

---

### Prompt 5B — Internal Tool Server

> Open: all files in `src/tools/internal/`

```
Implement the Internal tool server — gives agents access to the session's data.

schemas.py:
- GetPriorOutputInput(BaseModel): launch_id, agent_id
- SaveOutputInput(BaseModel): launch_id, agent_id, output: dict
- GetBriefInput(BaseModel): launch_id

tools.py — InternalToolExecutor(BaseMCPServer):
- execute(tool_name, inputs) -> dict dispatches to:
  - "get_prior_output": reads agent output from AgentRepository (via AsyncSessionLocal)
  - "save_output": writes output to AgentRepository
  - "get_brief": reads Launch from LaunchRepository
  - "get_session_data": reads from SessionStore (Redis)
  - "set_session_data": writes to SessionStore
- All DB operations use asyncio.run() since Lambda handlers are sync

server.py — defines the 5 tools with their input schemas as dicts (for passing to Anthropic API tools list)

INTERNAL_TOOLS list: the 5 tool dicts ready to be passed as tools=INTERNAL_TOOLS in API calls
```

---

### Prompt 5C — HubSpot, Slack, GA4 Servers

> Open all files in `src/tools/hubspot/`, `src/tools/slack/`, `src/tools/ga4/`

```
Implement 3 integration tool servers. Each follows the same pattern as TavilySearchExecutor.

HubSpot (src/tools/hubspot/):
- auth.py: get_hubspot_client(api_key) using hubspot-api-client SDK
- schemas.py: CreateContactInput, UpdateDealInput, GetContactInput
- tools.py — HubSpotExecutor: tools: create_contact, get_contact, create_deal, update_deal
- server.py: tool definitions for Anthropic API

Slack (src/tools/slack/):
- auth.py: get_slack_client(bot_token) using slack-sdk
- schemas.py: PostMessageInput (channel, text, blocks?), GetChannelInput
- tools.py — SlackExecutor: tools: post_message, get_channel_info, list_channels
- server.py: tool definitions

GA4 (src/tools/ga4/):
- auth.py: get_ga4_client(credentials) using google-analytics-data SDK
- schemas.py: GetMetricsInput (property_id, metrics, dimensions, date_range), MetricsResponse
- tools.py — GA4Executor: tools: ga4_get_metrics, ga4_get_events, ga4_get_conversions
- server.py: tool definitions

All executors: inherit BaseMCPServer, validate inputs with Pydantic before calling SDK, return dicts (not SDK objects), handle auth errors gracefully with {"error": "auth_failed"}.
Each tool server's auth tokens come from User.integrations JSON column (passed in payload by orchestrator).
```

---

## PHASE 6 — Frontend

### Prompt 6A — Next.js Config + Package Setup

> Open: `src/apps/web/package.json`, `src/apps/web/next.config.ts`, `src/apps/web/tailwind.config.ts`, `src/apps/web/tsconfig.json`

```
Set up the Next.js 15 frontend configuration files.

package.json — complete with:
{
  "name": "@launchiq/web",
  "scripts": { "dev": "next dev", "build": "next build", "lint": "next lint", "typecheck": "tsc --noEmit" },
  "dependencies": {
    "next": "15.x", "react": "19.x", "react-dom": "19.x",
    "@clerk/nextjs": "latest",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "latest", "clsx": "latest", "tailwind-merge": "latest",
    "lucide-react": "latest",
    "@radix-ui/react-dialog": "latest", "@radix-ui/react-badge": "latest"
  },
  "devDependencies": { "typescript": "^5.0.0", "@types/react": "^19.0.0", "@types/node": "^22.0.0" }
}

next.config.ts:
- Type: NextConfig
- rewrites: proxy /api/v1/* to process.env.API_URL/api/v1/* (for local dev CORS)
- env: expose NEXT_PUBLIC_API_URL, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

tailwind.config.ts:
- content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"]
- theme.extend.colors: { brand: { primary: "#6366f1", secondary: "#8b5cf6" } }

tsconfig.json:
- strict: true, target: "ES2022", paths: { "@/*": ["./*"] }
```

---

### Prompt 6B — Stores + API Client + SSE Hook

> Open: `src/apps/web/store/launchStore.ts`, `src/apps/web/store/agentStore.ts`, `src/apps/web/lib/api.ts`, `src/apps/web/lib/sse.ts`

```
Implement stores and client utilities.

store/launchStore.ts — useLaunchStore (Zustand):
- State: launch: Launch|null, agents: AgentRun[], hitl: HITLState|null, isStreaming: boolean
- Actions: setLaunch, updateAgent, setHITL, setStreaming, reset
- updateAgent: upsert by agent_id (update if exists, append if not)

store/agentStore.ts — useAgentStore (Zustand):
- State: events: AgentEvent[], currentAgent: AgentId|null
- AgentEvent type: {type: string, agent_id?: AgentId, output?: unknown, error?: string, timestamp: string}
- Actions: addEvent(event), setCurrentAgent, clearEvents

lib/api.ts — typed API client:
- createLaunch(data) -> Promise<{launch_id, status}>: POST /api/v1/launches
- getLaunch(launchId) -> Promise<LaunchDetailResponse>: GET /api/v1/launches/{id}
- resolveHITL(launchId, decision, edits?) -> Promise<{status, next_step}>: POST /api/v1/hitl/{id}/decide
- getPendingHITL(launchId) -> Promise<HITLState|null>: GET /api/v1/hitl/{id}/pending
- retryAgent(launchId, agentId) -> Promise<{status}>: POST /api/v1/agents/{launchId}/{agentId}/retry
- All functions: include Authorization header from Clerk getToken()
- Error handling: throw Error with parsed message on non-2xx

lib/sse.ts — useSSE React hook:
- useSSE(launchId: string|null, onEvent: (event: unknown) => void): void
- Creates EventSource to /api/v1/launches/{id}/stream
- Calls onEvent on each message (parse JSON)
- Auto-reconnect on error after SSE_RECONNECT_DELAY_MS
- Cleans up EventSource on unmount or launchId change
```

---

### Prompt 6C — Core Components

> Open all component files in `src/apps/web/components/`

```
Implement all UI components. Use Tailwind CSS + shadcn/ui patterns. No external component libraries beyond what's in package.json.

components/agents/AgentCard.tsx:
- Props: agent: AgentRun
- Shows: agent name (formatted), status badge, token count, completion time if done
- Status colors: pending=gray, running=blue (animated pulse), completed=green, failed=red
- Expand/collapse to show output JSON preview on click
- Running state: animated spinner + "Thinking..." text

components/agents/AgentPipeline.tsx:
- Props: agents: AgentRun[], currentAgent: AgentId|null
- Shows 4 AgentCards in vertical sequence with connecting arrows between them
- Highlights current running agent with glow effect
- Overall progress indicator (X/4 complete)

components/agents/AgentStream.tsx:
- Props: launchId: string
- Uses useSSE hook to subscribe to events
- Updates useLaunchStore and useAgentStore on each event
- Handles event types: agent_started, agent_completed, agent_failed, hitl_required, connected

components/hitl/HITLCheckpoint.tsx:
- Props: state: HITLState, onResolve: (decision, edits?) => void
- Full-page overlay (fixed inset-0 z-50 bg-black/50)
- Shows: checkpoint name, which agent produced this, output preview
- Contains HITLDecisionBar

components/hitl/HITLDecisionBar.tsx:
- Props: onApprove, onEdit, onReject (callbacks)
- Three buttons: Approve (green), Edit (yellow), Reject (red)
- Approve: calls onApprove directly
- Edit: opens HITLEditModal
- Reject: shows confirmation dialog before calling onReject
- Loading state while resolving

components/hitl/HITLEditModal.tsx:
- Props: initialData: Record<string,unknown>, onSave: (edits: Record<string,unknown>) => void, onClose
- Textarea showing JSON.stringify(initialData, null, 2) 
- Parse JSON on save, show validation error if invalid
- Save button calls onSave with parsed edits

components/launch/IntakeForm.tsx:
- Fields: product_name (text), description (textarea), target_market (text), competitors (tag input — type + Enter to add, X to remove)
- Validates all required fields before submit
- On submit: calls createLaunch() from api.ts, navigates to /launch/{id}/tracker
- Loading state during submission

components/launch/BriefCard.tsx — shows market intelligence output in card layout
components/launch/PersonaCard.tsx — shows a Persona with avatar initial, role, pain points, channels
components/launch/StrategyPhase.tsx — shows a LaunchPhase with timeline indicator
components/launch/ContentBlock.tsx — shows a ContentItem with format badge, headline, body, CTA
```

---

### Prompt 6D — Pages

> Open all page files in `src/apps/web/app/`

```
Implement all Next.js App Router pages.

app/(auth)/sign-in/page.tsx:
- Clerk <SignIn /> component centered on page

app/(auth)/sign-up/page.tsx:  
- Clerk <SignUp /> component centered on page

app/(app)/layout.tsx:
- Clerk <ClerkProvider> + sidebar navigation: Dashboard, New Launch
- User button in top-right
- Protected: redirect to /sign-in if not authenticated

app/(app)/dashboard/page.tsx:
- Fetch list of user's launches (GET /api/v1/launches)
- Show as table: product name, status badge, created date, View button
- "New Launch" CTA button → /launch/new
- Empty state: "No launches yet. Create your first one."

app/(app)/launch/new/page.tsx:
- Renders IntakeForm
- Full-page centered layout

app/(app)/launch/[id]/layout.tsx:
- Tab navigation: Brief | Personas | Strategy | Content | Tracker
- Fetch launch on mount, store in useLaunchStore
- Show loading skeleton while fetching

app/(app)/launch/[id]/tracker/page.tsx:
- Renders AgentStream (subscribes to SSE)
- Renders AgentPipeline
- If hitl !== null: renders HITLCheckpoint overlay
- On HITLCheckpoint resolve: calls resolveHITL() from api.ts
- Real-time status updates via useAgentStore events

app/(app)/launch/[id]/brief/page.tsx:
- Shows market intelligence output from launch.brief.market_data
- Uses BriefCard components

app/(app)/launch/[id]/personas/page.tsx:
- Shows audience insight output
- Grid of PersonaCard components

app/(app)/launch/[id]/strategy/page.tsx:
- Shows launch strategy phases
- Timeline of StrategyPhase components

app/(app)/launch/[id]/content/page.tsx:
- Shows content bundle
- Tabs: Email | Social | Ads
- Grid of ContentBlock components

app/(app)/settings/page.tsx:
- Integration cards for HubSpot, Slack, GA4
- Connect/disconnect buttons
- Show connected status from User.integrations

app/api/[...proxy]/route.ts:
- Proxy all requests to API_URL (avoids CORS in development)
- Pass Authorization header through
- Support GET, POST, PUT, DELETE
```

---

## PHASE 7 — Eval Framework

### Prompt 7A — Eval Core

> Open all files in `src/evals/framework/` and `src/evals/metrics/`

```
Implement the eval framework.

src/evals/metrics/relevance.py — RelevanceScorer:
- score(actual: dict, expected: dict) -> float: 
  - Convert both to strings, compute character-level overlap as a simple relevance proxy
  - Or: compare key field presence and value similarity
  - Returns 0.0 to 1.0

src/evals/metrics/hallucination.py — HallucinationScorer:
- score(output: dict, context: dict) -> float:
  - Check for hallucination signal phrases (model talking about itself, stale dates, etc.)
  - Returns rate: 0.0 = no hallucinations, 1.0 = all hallucinations
  - Uses the same patterns as src/agents/_base/output_validator.py

src/evals/metrics/schema_compliance.py — SchemaComplianceScorer:
- score(output: dict, schema_class: type[BaseModel]) -> float:
  - Returns 1.0 if Pydantic validation passes, 0.0 if it fails
  - Partial scores for partial compliance (some fields valid)

src/evals/metrics/edit_rate.py — EditRateScorer:
- score(original: dict, edited: dict) -> float:
  - Returns fraction of fields that were changed during HITL editing
  - 0.0 = no edits (best), 1.0 = all fields changed

src/evals/framework/scorer.py — Scorer:
- Wraps all 4 metrics
- score(actual, expected, context=None, schema_class=None) -> dict:
  Returns {"relevance_score": float, "hallucination_rate": float, "schema_compliance": float}

src/evals/framework/langfuse_client.py — LangfuseClient:
- __init__: creates Langfuse client from settings
- log(agent_id, test_case, output, scores) -> None: creates Langfuse trace + scores
- Gracefully no-ops if LANGFUSE keys not configured

src/evals/framework/reporter.py — Reporter:
- summarize(agent_id, results: list[dict]) -> dict: averages all scores, returns summary with pass/fail per metric
- print_report(summary: dict) -> None: formatted table output

src/evals/framework/evaluator.py — Evaluator:
- run_suite(agent_id, test_cases, expected) -> dict: runs all cases, scores each, returns summary
- _run_agent(agent_id, inputs) -> dict: dispatches via AgentDispatcher
```

---

### Prompt 7B — Test Cases + Regression Runner

> Open all files in `src/evals/suites/` and `src/evals/regression/`

```
Implement eval test cases and regression runner.

For each of the 4 agents, populate the JSON files:

src/evals/suites/market_intelligence/test_cases.json:
[
  {
    "id": "mi_001",
    "input": {
      "product_name": "LaunchIQ",
      "description": "AI-powered product launch intelligence platform",
      "target_market": "B2B SaaS founders and product marketers",
      "competitors": ["ProductBoard", "LaunchDarkly", "Wynter"]
    }
  }
]
(Add 3 more cases for different product types: consumer app, dev tool, marketplace)

src/evals/suites/market_intelligence/expected_outputs.json:
[
  {
    "market_size": "non-empty string",
    "growth_rate": "non-empty string",
    "competitors": [{"name": "string", "positioning": "string", "strengths": [], "weaknesses": []}],
    "trends": [{"trend": "string", "relevance": "string"}],
    "white_space": "non-empty string",
    "recommended_positioning": "non-empty string"
  }
]
(These are shape validators, not exact matches — evaluator checks structure + relevance)

Create similar test_cases.json and expected_outputs.json for: audience_insight, launch_strategy, content_generation suites.

src/evals/regression/baseline.json:
{
  "market_intelligence": {"relevance_score": 0.82, "hallucination_rate": 0.03, "schema_compliance": 1.00},
  "audience_insight":    {"relevance_score": 0.80, "hallucination_rate": 0.02, "schema_compliance": 1.00},
  "launch_strategy":     {"relevance_score": 0.85, "hallucination_rate": 0.04, "schema_compliance": 1.00},
  "content_generation":  {"relevance_score": 0.78, "hallucination_rate": 0.05, "schema_compliance": 1.00}
}

src/evals/regression/run_regression.py:
- CLI: python run_regression.py [--assert-baseline] [--agent AGENT_ID]
- Loads test cases + expected outputs from suites/
- Runs each agent via Evaluator
- Prints formatted table of scores vs baseline
- With --assert-baseline: exit(1) if any metric below baseline threshold

src/evals/regression/update_baseline.py:
- CLI: python update_baseline.py [--if-improved]
- Runs full suite, writes new baseline.json
- With --if-improved: only updates metrics that improved (never downgrades baseline)
```

---

## PHASE 8 — Infrastructure

### Prompt 8A — AWS CDK Stacks

> Open all files in `src/infra/aws/`

```
Implement AWS CDK infrastructure. Use aws-cdk-lib v2, Python.

src/infra/aws/app.py — CDK app entry point:
- Creates SecretsStack, DataStack, ApiStack, AgentsStack
- Pass stack outputs as cross-stack references

src/infra/aws/stacks/secrets_stack.py — SecretsStack:
- Creates Secrets Manager secrets:
  - launchiq/anthropic-api-key
  - launchiq/tavily-api-key
  - launchiq/clerk-secret-key
  - launchiq/database-url
- Expose as stack outputs

src/infra/aws/stacks/data_stack.py — DataStack:
- RDS PostgreSQL 16 (t3.micro for dev, r6g.large for prod) — use InstanceType
- ElastiCache Redis (cache.t3.micro for dev) — single node
- Both in private subnets (create VPC with 2 AZs)
- Security groups: DB only accessible from API/Worker SGs
- Expose: db_endpoint, redis_endpoint as outputs

src/infra/aws/stacks/api_stack.py — ApiStack:
- ECS Fargate service: API container (port 8000), Worker container (celery worker)
- ApplicationLoadBalancer: HTTPS on 443, redirect 80→443
- Task definition: 512 CPU, 1024 memory for both containers
- Environment: inject secrets from SecretsStack + endpoints from DataStack
- Auto-scaling: 1-4 tasks, scale on CPU 70%

src/infra/aws/stacks/agents_stack.py — AgentsStack:
- For each of 6 agents: aws_lambda.Function
  - function_name: launchiq-{agent_id}
  - runtime: PYTHON_3_12
  - handler: src.agents.{agent_id}.handler.handler
  - timeout: Duration.seconds(300)
  - memory: 1024
  - environment: inject ANTHROPIC_API_KEY, REDIS_URL, DATABASE_URL from secrets

src/infra/aws/constructs/agent_lambda.py — AgentLambdaConstruct(Construct):
- Reusable construct for a single agent Lambda
- Props: agent_id, secrets, environment_vars
- Creates Lambda + CloudWatch log group + IAM role with SecretsManager read permission

src/infra/aws/constructs/mcp_server.py — MCPServerConstruct(Construct):
- Lambda for MCP tool servers
- Same pattern as AgentLambdaConstruct
```

---

### Prompt 8B — Dockerfiles + CI/CD

> Open all Dockerfile + workflow files

```
Implement the remaining infrastructure files.

src/infra/docker/api.Dockerfile:
FROM python:3.12-slim
WORKDIR /app
COPY src/apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

src/infra/docker/worker.Dockerfile:
Same base, but CMD runs Celery worker:
celery -A src.apps.api.workers.celery_app.celery_app worker --loglevel=info --concurrency=2

src/infra/docker/mcp.Dockerfile:
Same base, CMD runs FastAPI MCP server:
uvicorn src.tools.internal.server:app --host 0.0.0.0 --port 8001

src/infra/vercel/vercel.json:
{
  "framework": "nextjs",
  "buildCommand": "pnpm build",
  "outputDirectory": ".next",
  "installCommand": "pnpm install",
  "env": {"NEXT_PUBLIC_API_URL": "@api-url", "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "@clerk-key"}
}

.github/workflows/deploy-staging.yml:
Same structure as deploy-production.yml but:
- Triggered on push to dev branch
- Deploys to launchiq-staging ECS cluster  
- Images tagged :staging
- No Slack notification
- Vercel --preview instead of --prod

.github/workflows/eval-scheduled.yml:
name: Scheduled Eval
on:
  schedule: [{cron: '0 9 * * 1'}]   # Monday 9am UTC
  workflow_dispatch: {}              # manual trigger
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - checkout + setup-python
      - pip install requirements
      - run_regression.py (with ANTHROPIC_API_KEY + LANGFUSE secrets)
      - update_baseline.py --if-improved
      - Upload report as artifact
      - Notify Slack on failure
```

---

## PHASE 9 — Integration & Polish

### Prompt 9A — Demo Data + Seed Script

> Open: create `src/data/` directory and files

```
Create demo seed data and seed script.

Create directory: src/data/demo/

src/data/demo/demo_launch.json:
LaunchIQ's own launch brief (dogfooding):
{
  "product_name": "LaunchIQ",
  "description": "AI-powered product launch intelligence platform that analyzes your market, builds buyer personas, creates a launch strategy, and generates launch content — all in under 10 minutes using a multi-agent AI pipeline.",
  "target_market": "B2B SaaS founders, product managers, and growth marketers at early-stage startups (Seed to Series A)",
  "competitors": ["ProductBoard", "Wynter", "GoPhraze", "Speeko", "FullStory"],
  "launch_date": "2026-06-01"
}

src/data/demo/demo_market_output.json:
Pre-computed realistic market intelligence output matching MarketIntelligenceOutput schema.
Include 4 real competitor analyses (ProductBoard, Wynter, etc.) with realistic data.
Market size: "$4.2B product management tools market, 18% YoY growth"
5 real trends relevant to AI-powered marketing tools in 2026.

src/data/demo/demo_personas.json:
Two complete personas matching AudienceInsightOutput:
1. "Sarah Chen" — Series A SaaS founder, 32-40, frustrated by manual launch prep
2. "Marcus Rivera" — Product marketer at 50-person startup, 28-35, needs speed + quality

src/data/seed.py:
- CLI: python seed.py [--demo] [--user-id USER_ID]
- --demo: creates a launch record with pre-computed outputs (skips API calls)
- Inserts into DB, sets all agent statuses to COMPLETED
- Prints launch_id for immediate demo use

Create Makefile at repo root:
dev: start docker-compose + api + celery + frontend
test: pytest src/ --cov=src
eval: python src/evals/regression/run_regression.py
migrate: alembic upgrade head
seed: python src/data/seed.py --demo
demo: make migrate && make seed && make dev
```

---

### Prompt 9B — Final Integration Test

> Use this after all phases complete

```
Write an end-to-end integration test in src/tests/test_e2e.py.

Test: full_pipeline_e2e
1. Start with demo brief from src/data/demo/demo_launch.json
2. POST to /api/v1/launches — verify 201 + launch_id returned
3. Poll GET /api/v1/launches/{id} every 2s for max 60s
4. Verify status reaches "hitl_pending" (after market_intelligence)
5. POST /api/v1/hitl/{id}/decide with decision="approve"
6. Continue polling — verify status reaches "hitl_pending" again (after launch_strategy)
7. POST approve again
8. Continue polling — verify status reaches "completed"
9. GET /api/v1/launches/{id} — verify all 4 agents have status="completed"
10. Verify brief_output contains all 4 agent outputs

Mark test with @pytest.mark.integration — excluded from unit test runs, included in CI eval gate.
Requires: running API (localhost:8000), Redis, PostgreSQL — use docker-compose.

Also write smoke test in src/tests/test_smoke.py:
- GET /api/v1/health → 200, status=ok
- GET /api/v1/health/ready → 200, status=ready
- POST /api/v1/launches with missing fields → 422
- GET /api/v1/launches/nonexistent → 404
```

---

## Quick Reference — File → Phase Map

| File / Directory | Phase |
|-----------------|-------|
| `src/packages/` | 1 |
| `src/apps/api/models/` | 1 |
| `src/memory/structured/` | 1 |
| `src/memory/short_term/` | 1 |
| `src/memory/long_term/` | 1 |
| `src/apps/api/middleware/` | 2 |
| `src/apps/api/services/` | 2 |
| `src/apps/api/routers/integrations.py` | 2 |
| `src/agents/orchestrator/` | 3 |
| `src/apps/api/workers/` | 3 |
| `src/agents/market_intelligence/` | 4 |
| `src/agents/audience_insight/` | 4 |
| `src/agents/launch_strategy/` | 4 |
| `src/agents/content_generation/` | 4 |
| `src/agents/analytics_feedback/` | 4 |
| `src/tools/` | 5 |
| `src/apps/web/` | 6 |
| `src/evals/` | 7 |
| `src/infra/` | 8 |
| `src/data/`, `Makefile` | 9 |

---

## Already Implemented (do NOT re-implement)

| File | Status |
|------|--------|
| `src/agents/_base/base_agent.py` | Complete |
| `src/agents/_base/cognitive_loop.py` | Complete |
| `src/agents/_base/context_builder.py` | Complete |
| `src/agents/_base/output_validator.py` | Complete |
| `src/apps/api/main.py` | Complete |
| `src/apps/api/config.py` | Complete |
| `src/apps/api/routers/health.py` | Complete |
| `src/apps/api/routers/launches.py` | Complete |
| `src/apps/api/routers/agents.py` | Complete |
| `src/apps/api/routers/hitl.py` | Complete |
