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

## PHASE 6 — Frontend (Modern 2026)

> **Stack:** Next.js 15 (App Router + PPR) · React 19 · Tailwind CSS v4 · shadcn/ui · Zustand v5 · TanStack Query v5 · Clerk · openapi-typescript

---

### Prompt 6A — Package Setup + Config

> Open: `src/apps/web/package.json`, `src/apps/web/next.config.ts`, `src/apps/web/tailwind.config.ts`, `src/apps/web/tsconfig.json`

```
Set up the Next.js 15 + React 19 frontend for 2026. Use the exact versions below.

package.json:
{
  "name": "@launchiq/web",
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "generate:api-types": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts"
  },
  "dependencies": {
    "next": "15.3.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "@clerk/nextjs": "^6.0.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-query-devtools": "^5.0.0",
    "react-hook-form": "^7.54.0",
    "zod": "^3.24.0",
    "@hookform/resolvers": "^3.9.0",
    "nuqs": "^2.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0",
    "lucide-react": "^0.468.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.1.0",
    "@radix-ui/react-tooltip": "^1.1.0",
    "@radix-ui/react-avatar": "^1.1.0",
    "@radix-ui/react-badge": "^1.0.0",
    "@radix-ui/react-separator": "^1.1.0",
    "sonner": "^1.7.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "@types/react": "^19.0.0",
    "@types/node": "^22.0.0",
    "openapi-typescript": "^7.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "15.3.0"
  }
}

next.config.ts:
import type { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    ppr: true,               // Partial Prerendering — static shell + streaming dynamic parts
    reactCompiler: true,     // React 19 compiler — auto-memoization
    typedRoutes: true,       // Compile-time route type safety
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.API_URL ?? 'http://localhost:8000'}/api/v1/:path*`,
      },
    ]
  },
}
export default config

tailwind.config.ts (Tailwind v4 — CSS-first, minimal JS config):
import type { Config } from 'tailwindcss'

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary:   'oklch(0.55 0.22 264)',
          secondary: 'oklch(0.60 0.20 290)',
          accent:    'oklch(0.70 0.18 200)',
        },
      },
      animation: {
        'pulse-slow':   'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'thinking':     'thinking 1.5s ease-in-out infinite',
        'slide-in':     'slideIn 0.2s ease-out',
      },
      keyframes: {
        thinking: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.3' },
        },
        slideIn: {
          from: { transform: 'translateY(8px)', opacity: '0' },
          to:   { transform: 'translateY(0)',   opacity: '1' },
        },
      },
    },
  },
} satisfies Config

tsconfig.json:
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "ES2022"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  }
}

Also create src/apps/web/app/globals.css:
@import "tailwindcss";

@theme {
  --color-brand-primary:   oklch(0.55 0.22 264);
  --color-brand-secondary: oklch(0.60 0.20 290);
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --radius-default: 0.625rem;
}

Also create middleware.ts at src/apps/web/ root (Clerk 2026 pattern):
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublic = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/v1/health(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublic(req)) await auth.protect()
})

export const config = {
  matcher: ['/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)', '/(api|trpc)(.*)'],
}
```

---

### Prompt 6B — Auto-generated API Types + Query Client

> Create: `src/apps/web/src/types/api.ts` (auto-generated), `src/apps/web/lib/query-client.ts`, `src/apps/web/lib/api.ts`, `src/apps/web/app/providers.tsx`

```
Set up end-to-end type safety using openapi-typescript + TanStack Query v5.

STEP 1 — Generate types from FastAPI (run this command first):
  pnpm generate:api-types
This creates src/types/api.ts from http://localhost:8000/openapi.json automatically.
If API is not running yet, create a placeholder src/types/api.ts:
  export type paths = Record<string, unknown>
  export type components = { schemas: Record<string, unknown> }

STEP 2 — lib/query-client.ts:
Create a singleton QueryClient with these defaults:
- staleTime: 30_000 (30s — avoid over-fetching for AI outputs)
- retry: 1
- refetchOnWindowFocus: false (agent outputs don't change while tab is hidden)

Export: getQueryClient() that returns singleton on server, new instance on client.

STEP 3 — lib/api.ts (typed fetch client using generated types):
Import paths from src/types/api.ts.

Implement these typed functions using native fetch:

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T>
- Gets Clerk token: const { getToken } = await import('@clerk/nextjs/server') on server
  OR useAuth() hook token on client — detect via typeof window
- Sets Authorization: Bearer {token} header
- Throws ApiError (custom class with status + message) on non-2xx
- Returns parsed JSON as T

Export:
- createLaunch(data: LaunchBriefRequest): POST /api/v1/launches → Launch
- getLaunch(id: string): GET /api/v1/launches/{id} → LaunchDetailResponse
- listLaunches(): GET /api/v1/launches → Launch[]
- resolveHITL(id: string, body: HITLDecision): POST /api/v1/hitl/{id}/decide
- getPendingHITL(id: string): GET /api/v1/hitl/{id}/pending → HITLState | null
- retryAgent(launchId: string, agentId: string): POST /api/v1/agents/{launchId}/{agentId}/retry
- listIntegrations(): GET /api/v1/integrations → {hubspot: bool, slack: bool, ga4: bool}
- connectIntegration(name: string, creds: object): POST /api/v1/integrations/{name}
- disconnectIntegration(name: string): DELETE /api/v1/integrations/{name}

All types reference the generated api.ts types. No manual type duplication.

STEP 4 — app/providers.tsx (React 19 pattern):
'use client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { getQueryClient } from '@/lib/query-client'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  )
}
```

---

### Prompt 6C — Zustand Stores + SSE Hook

> Open: `src/apps/web/store/launchStore.ts`, `src/apps/web/store/agentStore.ts`, `src/apps/web/lib/sse.ts`

```
Implement Zustand v5 stores and SSE hook using 2026 patterns.

store/launchStore.ts — Zustand v5 with immer middleware:
import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { Launch, AgentRun, HITLState, AgentId } from '@/src/packages/types'

interface LaunchStore {
  launch:      Launch | null
  agents:      AgentRun[]
  hitl:        HITLState | null
  isStreaming: boolean
  // Actions
  setLaunch:     (l: Launch) => void
  upsertAgent:   (a: AgentRun) => void   // insert or update by agent_id
  setHITL:       (h: HITLState | null) => void
  setStreaming:   (v: boolean) => void
  reset:         () => void
}

export const useLaunchStore = create<LaunchStore>()(
  immer((set) => ({
    launch: null, agents: [], hitl: null, isStreaming: false,
    setLaunch:   (l) => set((s) => { s.launch = l }),
    upsertAgent: (a) => set((s) => {
      const idx = s.agents.findIndex((x) => x.agent_id === a.agent_id)
      if (idx >= 0) s.agents[idx] = a
      else s.agents.push(a)
    }),
    setHITL:     (h) => set((s) => { s.hitl = h }),
    setStreaming: (v) => set((s) => { s.isStreaming = v }),
    reset:       () => set(() => ({ launch: null, agents: [], hitl: null, isStreaming: false })),
  }))
)

store/agentStore.ts — event log store:
interface AgentEvent {
  type:      string
  agent_id?: AgentId
  output?:   unknown
  error?:    string
  timestamp: string
}
interface AgentStore {
  events:        AgentEvent[]
  currentAgent:  AgentId | null
  addEvent:      (e: AgentEvent) => void
  setCurrentAgent: (id: AgentId | null) => void
  clearEvents:   () => void
}
Use immer middleware. addEvent appends with timestamp = new Date().toISOString().

lib/sse.ts — useSSE hook (React 19, no useEffect anti-patterns):
'use client'
import { useEffect, useRef, useCallback } from 'react'

const SSE_RECONNECT_MS = 3000

export function useSSE(
  launchId: string | null,
  onEvent: (event: unknown) => void
): { connected: boolean } {
  const esRef      = useRef<EventSource | null>(null)
  const retryRef   = useRef<ReturnType<typeof setTimeout> | null>(null)
  const connRef    = useRef(false)

  const connect = useCallback(() => {
    if (!launchId) return
    esRef.current?.close()

    const url = `/api/v1/launches/${launchId}/stream`
    const es  = new EventSource(url)
    esRef.current = es

    es.onopen    = () => { connRef.current = true }
    es.onmessage = (e) => {
      try { onEvent(JSON.parse(e.data)) } catch {}
    }
    es.onerror = () => {
      connRef.current = false
      es.close()
      retryRef.current = setTimeout(connect, SSE_RECONNECT_MS)
    }
  }, [launchId, onEvent])

  useEffect(() => {
    connect()
    return () => {
      esRef.current?.close()
      if (retryRef.current) clearTimeout(retryRef.current)
    }
  }, [connect])

  return { connected: connRef.current }
}
```

---

### Prompt 6D — AI-Native Components (2026 Patterns)

> Open all files in `src/apps/web/components/`

```
Implement all UI components using 2026 AI-native patterns.
Use Tailwind CSS v4 + shadcn/ui primitives (Button, Card, Badge, Dialog, Tabs from @radix-ui).
Use lucide-react for icons. Use sonner for toast notifications.

--- AGENT COMPONENTS ---

components/agents/AgentCard.tsx:
Props: agent: AgentRun
2026 AI-native patterns to apply:
- Status badge: pending=slate, running=blue+animate-pulse, completed=emerald, failed=red, skipped=slate/50
- Running state: show "Thinking..." with animate-thinking dots + brain icon from lucide
- Tool call badges: if agent.output?.tool_calls, show each tool called as a small badge (e.g. "tavily_search ×3")
- Token counter: show tokens_used with sparkles icon — animate count-up from 0 when completed
- Completion time: show duration in seconds (completed_at - started_at)
- Expand: click card body to reveal output as syntax-highlighted JSON (use <pre className="text-xs overflow-auto max-h-64">)
- Glow effect when running: ring-2 ring-blue-400/50 shadow-blue-400/20 shadow-lg

components/agents/AgentPipeline.tsx:
Props: agents: AgentRun[], currentAgent: AgentId | null
- Vertical sequence of AgentCards with animated connector lines between them
- Connector line color: completed=emerald, active=blue animated dashes, pending=slate
- Progress bar at top: "2 / 4 agents complete" with emerald fill
- Overall status chip: "Running Market Intelligence..." or "All agents complete ✓"
- Animate slide-in for each card as agents are added (animate-slide-in)

components/agents/AgentStream.tsx:
Props: launchId: string
- Subscribes to useSSE, routes events to stores
- Event routing:
  connected       → setStreaming(true)
  agent_started   → upsertAgent({...agent, status:'running', started_at: now})
                    setCurrentAgent(agent_id)
  agent_completed → upsertAgent({...agent, status:'completed', output, tokens_used})
                    setCurrentAgent(null)
  agent_failed    → upsertAgent({...agent, status:'failed', error})
                    toast.error(`${agent_id} failed: ${error}`)
  hitl_required   → setHITL(checkpoint_state)
                    toast.info("Action required: Review and approve to continue")
  error           → toast.error(message)
- Returns null (no visual output — side-effects only)

--- HITL COMPONENTS (2026 Human-in-the-Loop patterns) ---

components/hitl/HITLCheckpoint.tsx:
Props: state: HITLState, onResolve: (decision: HITLDecision, edits?: Record<string,unknown>) => void
- Full-page modal overlay: fixed inset-0 z-50, backdrop-blur-sm bg-black/60
- Slide-up card: max-w-2xl mx-auto mt-20 animate-slide-in
- Header: yellow warning banner "Action Required" + checkpoint name + agent that produced it
- Body: scrollable output preview (JSON rendered as readable key-value pairs, not raw JSON)
- Contains HITLDecisionBar at bottom
- Trap focus inside modal (Radix Dialog handles this)
- Press Escape = open reject confirmation

components/hitl/HITLDecisionBar.tsx:
Props: onApprove: () => void, onEdit: () => void, onReject: () => void, isPending: boolean
- Three-button row at bottom of HITL overlay
- Approve: emerald button + CheckCircle icon — calls onApprove
- Edit:    yellow button + PencilLine icon — calls onEdit (opens HITLEditModal)
- Reject:  red outline button + XCircle icon — opens confirmation AlertDialog before calling onReject
- All buttons disabled + show Loader2 spinner when isPending=true
- Keyboard: Enter = approve, E = edit, Escape = reject confirmation

components/hitl/HITLEditModal.tsx:
Props: initialData: Record<string,unknown>, onSave: (edits: Record<string,unknown>) => void, onClose: () => void
- Radix Dialog inside the HITLCheckpoint overlay
- Textarea: monospace font, pre-filled with JSON.stringify(initialData, null, 2)
- Live validation: parse JSON on change, show red border + error message if invalid
- Diff preview: show which keys changed vs original (highlight changed lines in yellow)
- Save button: disabled if JSON invalid, calls onSave(parsed) on click
- Cancel button: calls onClose

--- LAUNCH COMPONENTS ---

components/launch/IntakeForm.tsx:
Use React Hook Form + Zod for validation.

Schema (define inline):
const schema = z.object({
  product_name:  z.string().min(2).max(100),
  description:   z.string().min(20).max(1000),
  target_market: z.string().min(5).max(200),
  competitors:   z.array(z.string()).max(10).default([]),
  launch_date:   z.string().optional(),
})

UI:
- product_name: text input + label
- description: textarea (4 rows) + character counter
- target_market: text input
- competitors: tag input — type competitor name + Enter/comma to add, × to remove each tag
  Store as controlled array, render as Badge list with × button
- launch_date: date input (optional)
- Submit: calls createLaunch(data) → on success: router.push(`/launch/${id}/tracker`)
  Show Loader2 in button while submitting
- Field errors: show below each field using react-hook-form formState.errors
- Form-level error: show toast.error on API failure

components/launch/BriefCard.tsx:
Props: data: MarketData
- Card with market size, growth rate as prominent stats
- Competitor grid: each competitor as a mini-card (name, positioning badge, strength/weakness chips)
- Trends list: each trend with relevance score pill
- White space + positioning in highlighted callout box

components/launch/PersonaCard.tsx:
Props: persona: Persona, isPrimary?: boolean
- Avatar: large initial letter circle with gradient background
- Role + age range as subtitle
- Pain points: red dot list
- Goals: green dot list
- Channels: icon badges (LinkedIn, Twitter, Email etc)
- Message hook: italic quote block
- "Primary" badge if isPrimary=true

components/launch/StrategyPhase.tsx:
Props: phase: LaunchPhase, index: number, isActive?: boolean
- Timeline item: left vertical line + numbered circle
- Phase name + duration as header
- Goals, tactics, KPIs as collapsible sections
- isActive: highlight with brand-primary border

components/launch/ContentBlock.tsx:
Props: item: ContentItem
- Format badge (Email/LinkedIn/Twitter/Ad Copy) + variant pill (A/B)
- Headline: large bold text
- Body: paragraph with line clamp (expand on click)
- CTA: button-style chip
- Target persona tag
- Copy-to-clipboard button on hover (uses navigator.clipboard)
```

---

### Prompt 6E — Pages (Server Components + Streaming)

> Open all page files in `src/apps/web/app/`

```
Implement all Next.js 15 App Router pages using 2026 patterns.
Default = Server Components. Add "use client" ONLY where interactivity is needed.
Use TanStack Query for client data, direct async fetch for server data.

--- AUTH PAGES ---

app/(auth)/sign-in/page.tsx — Server Component:
import { SignIn } from '@clerk/nextjs'
export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 to-slate-900">
      <SignIn routing="hash" />
    </div>
  )
}

app/(auth)/sign-up/page.tsx — same pattern with <SignUp />

--- APP SHELL ---

app/(app)/layout.tsx — Server Component:
- Import ClerkProvider, wrap entire layout
- Server-side auth check: redirect('/sign-in') if no userId
- Sidebar: links to Dashboard + New Launch
- UserButton from Clerk in top-right
- Render {children} in main content area
- Use Suspense with skeleton fallback around {children}

app/(app)/dashboard/page.tsx — Server Component (direct async fetch):
- async function DashboardPage()
- const launches = await listLaunches()  — direct server-side fetch with Clerk server token
- Render LaunchTable (client component for sorting/filtering) with initial data
- "New Launch" button → /launch/new
- If launches.length === 0: show EmptyState component

Create components/launch/LaunchTable.tsx — Client Component:
- Columns: Product Name, Status badge, Created date, View button
- Client-side sort by created_at (useLocalSort hook)
- Row click → router.push(/launch/{id}/tracker)

--- LAUNCH PAGES ---

app/(app)/launch/new/page.tsx — Server Component wrapper:
- export const metadata = { title: 'New Launch — LaunchIQ' }
- Render <IntakeForm /> (which is 'use client')
- Center vertically, max-w-xl

app/(app)/launch/[id]/layout.tsx — Server Component:
- Fetch launch server-side: const launch = await getLaunch(params.id)
- If not found: notFound()
- Pass launch to client store via <LaunchInitializer launch={launch} /> (tiny client component that calls setLaunch on mount)
- Tab nav: Brief | Personas | Strategy | Content | Tracker
  Use Next.js <Link> for each tab — active tab highlighted by comparing pathname
- Show launch status badge next to product name in header

app/(app)/launch/[id]/tracker/page.tsx — Client Component ('use client'):
- This is the real-time page — must be client
- Renders <AgentStream launchId={id} /> (subscribes to SSE, updates stores)
- Renders <AgentPipeline agents={agents} currentAgent={currentAgent} /> from store
- If hitl !== null: renders <HITLCheckpoint state={hitl} onResolve={handleResolve} />
- handleResolve: calls resolveHITL() → on success: setHITL(null) + toast.success
- Show "Launch complete! View your brief →" banner when all agents done

app/(app)/launch/[id]/brief/page.tsx — Server Component:
- const launch = await getLaunch(params.id)
- If no market data: show <AgentPending agentName="Market Intelligence" />
- Else: render <BriefCard data={launch.brief.market_data} />
- Wrap in Suspense with skeleton

app/(app)/launch/[id]/personas/page.tsx — Server Component:
- Grid of <PersonaCard> — primary first, then secondary
- If no personas: show <AgentPending agentName="Audience Insight" />

app/(app)/launch/[id]/strategy/page.tsx — Server Component:
- Vertical timeline of <StrategyPhase> components
- Budget allocation as a horizontal bar chart (use CSS widths — no chart library)
- Risk list in red callout box

app/(app)/launch/[id]/content/page.tsx — Client Component:
- Tabs: Email | Social | Ads (Radix Tabs)
- Each tab: grid of <ContentBlock> items
- "Copy All" button per tab — copies all content as formatted text
- If no content: show <AgentPending agentName="Content Generation" />

app/(app)/settings/page.tsx — Client Component:
- Integration cards for HubSpot, Slack, GA4
- Each card: logo, name, description, status (connected/disconnected)
- Connect button: opens modal to enter credentials
- Disconnect: confirmation dialog → calls disconnectIntegration()
- Use useQuery to fetch /api/v1/integrations for real-time connected status

--- SHARED COMPONENTS TO CREATE ---

components/ui/AgentPending.tsx:
Props: agentName: string
- Centered card: clock icon + "Waiting for {agentName} to complete..."
- Subtle animate-pulse

components/ui/EmptyState.tsx:
Props: title, description, action?: { label, href }
- Centered illustration (use lucide RocketIcon) + text + optional CTA button

components/ui/LaunchInitializer.tsx ('use client'):
- Takes launch prop, calls useLaunchStore.setLaunch(launch) on mount
- Returns null — side effect only

app/api/[...proxy]/route.ts:
- Proxy /api/v1/* requests to process.env.API_URL
- Forward Authorization header from incoming request
- Support GET, POST, PUT, DELETE, PATCH
- Set no-store cache for all proxied responses

--- EXIT CRITERIA ---
- pnpm typecheck passes with 0 errors
- pnpm build completes successfully  
- pnpm lint passes
- Dashboard loads launches from server
- Tracker page shows live agent updates via SSE
- HITL overlay appears and resolves correctly
- All 5 worker pages show correct data or AgentPending fallback
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
