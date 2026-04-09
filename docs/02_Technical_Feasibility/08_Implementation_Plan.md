# LaunchIQ — Implementation Plan (Phase-wise)

> **Purpose:** Step-by-step build guide for GitHub Copilot and human developers.
> Each phase is self-contained, has clear entry/exit criteria, and maps directly to files in `src/`.
> Complete phases in order — later phases depend on earlier foundations.

---

## Repository Quick Reference

```
src/
├── agents/           # 6 AI agents (Python) — Lambda-deployed
│   ├── _base/        # Shared: BaseAgent, CognitiveLoop, ContextBuilder, OutputValidator
│   ├── orchestrator/
│   ├── market_intelligence/
│   ├── audience_insight/
│   ├── launch_strategy/
│   ├── content_generation/
│   └── analytics_feedback/
├── apps/
│   ├── api/          # FastAPI backend — ECS Fargate
│   └── web/          # Next.js 15 frontend — Vercel
├── tools/            # MCP tool servers (Tavily, HubSpot, Slack, GA4, Internal)
├── memory/           # Redis (short-term) | Qdrant (long-term) | PostgreSQL (structured)
├── packages/         # Shared types, config, utils
├── evals/            # Eval framework + per-agent suites + regression gate
└── infra/            # AWS CDK stacks + Dockerfiles + Vercel config
```

---

## Phase Overview

| Phase | Name | Deliverable | Est. Effort |
|-------|------|-------------|-------------|
| 1 | Foundation & Data Layer | DB models, migrations, repositories, Redis/Qdrant clients | Medium |
| 2 | API Core | All FastAPI middleware, services, routers working end-to-end | Medium |
| 3 | Agent Foundation | BaseAgent complete, Orchestrator agent + workflow state | High |
| 4 | Worker Agents | All 5 worker agents with schemas, prompts, tool calls | High |
| 5 | MCP Tool Servers | Tavily, HubSpot, Slack, GA4, Internal tools | Medium |
| 6 | Frontend | Next.js pages, SSE streaming, HITL UI, Zustand stores | High |
| 7 | Eval Framework | Per-agent suites, regression gate, Langfuse integration | Medium |
| 8 | Infrastructure | AWS CDK stacks, Dockerfiles, CI/CD workflows | Medium |
| 9 | Integration & Polish | E2E test, demo data, README polish, deployment | Low |

---

## Phase 1 — Foundation & Data Layer

**Goal:** All database models, migrations, and repository layer working. This is the data contract that every other layer depends on.

### 1.1 Shared Types (`src/packages/`)

**File: `src/packages/types/launch.ts`**
```typescript
// TypeScript types shared between frontend and API proxy
export interface Launch {
  launch_id: string;
  status: 'pending' | 'running' | 'hitl_pending' | 'completed' | 'failed';
  product_name: string;
  description: string;
  target_market: string;
  competitors: string[];
  launch_date?: string;
  created_at: string;
  updated_at: string;
}

export interface LaunchBrief {
  launch_id: string;
  market_data?: MarketData;
  personas?: Persona[];
  strategy?: LaunchStrategy;
  content?: ContentBundle;
}
```

**File: `src/packages/types/agent.ts`**
```typescript
export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
export type AgentId =
  | 'orchestrator'
  | 'market_intelligence'
  | 'audience_insight'
  | 'launch_strategy'
  | 'content_generation'
  | 'analytics_feedback';

export interface AgentRun {
  agent_id: AgentId;
  launch_id: string;
  status: AgentStatus;
  output?: Record<string, unknown>;
  tokens_used?: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
}
```

**File: `src/packages/types/hitl.ts`**
```typescript
export type HITLDecision = 'approve' | 'edit' | 'reject';
export type HITLCheckpoint =
  | 'brief_review'
  | 'persona_review'
  | 'strategy_review'
  | 'content_review';

export interface HITLState {
  launch_id: string;
  checkpoint: HITLCheckpoint;
  agent_id: AgentId;
  output_preview: Record<string, unknown>;
  decision?: HITLDecision;
  edits?: Record<string, unknown>;
  created_at: string;
  resolved_at?: string;
}
```

**File: `src/packages/config/models.py`**
```python
# Model assignments per agent — single source of truth
AGENT_MODELS = {
    "orchestrator":        "claude-opus-4-6",
    "market_intelligence": "claude-sonnet-4-6",
    "audience_insight":    "claude-sonnet-4-6",
    "launch_strategy":     "claude-opus-4-6",
    "content_generation":  "claude-sonnet-4-6",
    "analytics_feedback":  "claude-haiku-4-5-20251001",
}

HITL_CHECKPOINTS = [
    "brief_review",
    "persona_review",
    "strategy_review",
    "content_review",
]
```

**File: `src/packages/utils/logger.py`**
```python
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    return logger
```

**File: `src/packages/utils/retry.py`**
```python
import asyncio
import functools
from typing import Callable, TypeVar

T = TypeVar("T")

def with_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator — retries async functions on exception with exponential backoff."""
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            attempt = 0
            wait = delay
            while attempt < max_attempts:
                try:
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    attempt += 1
                    if attempt == max_attempts:
                        raise
                    await asyncio.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
```

**File: `src/packages/utils/token_counter.py`**
```python
# Approximate token counter (no tiktoken dependency)
# Uses 4 chars ≈ 1 token heuristic for budget warnings
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def estimate_messages_tokens(messages: list[dict]) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    total += estimate_tokens(block.get("text", ""))
    return total
```

---

### 1.2 Database Models (`src/apps/api/models/`)

**File: `src/apps/api/models/launch.py`**
```python
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class LaunchStatus(str, Enum):
    PENDING      = "pending"
    RUNNING      = "running"
    HITL_PENDING = "hitl_pending"
    COMPLETED    = "completed"
    FAILED       = "failed"

class Launch(Base):
    __tablename__ = "launches"

    launch_id    = Column(String(36), primary_key=True)
    user_id      = Column(String(255), nullable=False, index=True)
    status       = Column(String(50), default=LaunchStatus.PENDING)
    product_name = Column(String(255), nullable=False)
    description  = Column(Text, nullable=False)
    target_market= Column(String(255), nullable=False)
    competitors  = Column(JSON, default=list)
    launch_date  = Column(String(50), nullable=True)
    brief_output = Column(JSON, nullable=True)      # orchestrator output
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**File: `src/apps/api/models/agent.py`**
```python
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from .launch import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    launch_id    = Column(String(36), nullable=False, index=True)
    agent_id     = Column(String(100), nullable=False)
    status       = Column(String(50), default="pending")
    output       = Column(JSON, nullable=True)
    tokens_used  = Column(Integer, default=0)
    error        = Column(Text, nullable=True)
    started_at   = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
```

**File: `src/apps/api/models/hitl.py`**
```python
from datetime import datetime
from sqlalchemy import Column, DateTime, String, JSON, Text
from .launch import Base

class HITLCheckpointRecord(Base):
    __tablename__ = "hitl_checkpoints"

    id              = Column(String(36), primary_key=True)
    launch_id       = Column(String(36), nullable=False, index=True)
    checkpoint      = Column(String(100), nullable=False)
    agent_id        = Column(String(100), nullable=False)
    output_preview  = Column(JSON, nullable=False)
    decision        = Column(String(50), nullable=True)   # approve/edit/reject
    edits           = Column(JSON, nullable=True)
    comment         = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    resolved_at     = Column(DateTime, nullable=True)
```

**File: `src/apps/api/models/user.py`**
```python
from datetime import datetime
from sqlalchemy import Column, DateTime, String, JSON
from .launch import Base

class User(Base):
    __tablename__ = "users"

    user_id       = Column(String(255), primary_key=True)  # Clerk user ID
    email         = Column(String(255), unique=True, nullable=False)
    plan          = Column(String(50), default="free")
    integrations  = Column(JSON, default=dict)  # {hubspot: {...}, slack: {...}}
    created_at    = Column(DateTime, default=datetime.utcnow)
```

---

### 1.3 Database Connection (`src/memory/structured/database.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.apps.api.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,   # Lambda-safe: no persistent connections
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

---

### 1.4 Migrations (`src/memory/structured/migrations/`)

Use Alembic. Run these commands to scaffold:
```bash
# From src/memory/structured/
alembic init migrations
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

Configure `alembic.ini` to point at `settings.database_url`.
Configure `env.py` to import `Base` from `src/apps/api/models/launch.py`.

---

### 1.5 Repositories (`src/memory/structured/repositories/`)

Each repository wraps SQLAlchemy queries. Pattern for all 6 repos:

**File: `src/memory/structured/repositories/launch_repo.py`**
```python
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.api.models.launch import Launch, LaunchStatus


class LaunchRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_id: str, data: dict[str, Any]) -> Launch:
        launch = Launch(
            launch_id=str(uuid.uuid4()),
            user_id=user_id,
            **data,
        )
        self.db.add(launch)
        await self.db.commit()
        await self.db.refresh(launch)
        return launch

    async def get(self, launch_id: str) -> Launch | None:
        result = await self.db.execute(
            select(Launch).where(Launch.launch_id == launch_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, launch_id: str, status: LaunchStatus) -> None:
        await self.db.execute(
            update(Launch)
            .where(Launch.launch_id == launch_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def save_brief_output(self, launch_id: str, output: dict) -> None:
        await self.db.execute(
            update(Launch)
            .where(Launch.launch_id == launch_id)
            .values(brief_output=output, updated_at=datetime.utcnow())
        )
        await self.db.commit()
```

Follow the same pattern for: `agent_repo.py`, `hitl_repo.py`, `brief_repo.py`, `persona_repo.py`, `strategy_repo.py`, `content_repo.py`.

---

### 1.6 Redis Client (`src/memory/short_term/session_store.py`)

```python
from __future__ import annotations
import json
import redis.asyncio as aioredis
from src.apps.api.config import get_settings

settings = get_settings()
_redis: aioredis.Redis | None = None

def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis

class SessionStore:
    KEY_PREFIX = "session:"
    TTL = 3600  # 1 hour

    def __init__(self) -> None:
        self.redis = get_redis()

    async def set(self, launch_id: str, key: str, value: dict) -> None:
        field = f"{self.KEY_PREFIX}{launch_id}:{key}"
        await self.redis.setex(field, self.TTL, json.dumps(value))

    async def get(self, launch_id: str, key: str) -> dict | None:
        field = f"{self.KEY_PREFIX}{launch_id}:{key}"
        data = await self.redis.get(field)
        return json.loads(data) if data else None

    async def publish(self, channel: str, event: dict) -> None:
        """Publish SSE event to Redis pub/sub channel."""
        await self.redis.publish(channel, json.dumps(event))
```

**File: `src/memory/short_term/hitl_state.py`**
```python
# Stores pending HITL checkpoint in Redis — pipeline polls this
# Key: hitl:{launch_id}  Value: HITLState JSON  TTL: 24h

from __future__ import annotations
import json
from .session_store import get_redis

class HITLStateStore:
    KEY_PREFIX = "hitl:"
    TTL = 86400  # 24 hours

    def __init__(self) -> None:
        self.redis = get_redis()

    async def set_pending(self, launch_id: str, state: dict) -> None:
        await self.redis.setex(f"{self.KEY_PREFIX}{launch_id}", self.TTL, json.dumps(state))

    async def get_pending(self, launch_id: str) -> dict | None:
        data = await self.redis.get(f"{self.KEY_PREFIX}{launch_id}")
        return json.loads(data) if data else None

    async def clear(self, launch_id: str) -> None:
        await self.redis.delete(f"{self.KEY_PREFIX}{launch_id}")
```

---

### 1.7 Qdrant Client (`src/memory/long_term/qdrant_client.py`)

```python
from __future__ import annotations
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.apps.api.config import get_settings
import anthropic
import uuid

settings = get_settings()

_qdrant: AsyncQdrantClient | None = None

def get_qdrant() -> AsyncQdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    return _qdrant

async def embed(text: str) -> list[float]:
    """Embed text using Anthropic's text-embedding model."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    # Use voyage-3 via Anthropic API
    response = client.beta.messages.batches  # placeholder — use actual embedding endpoint
    # For now: use openai text-embedding-3-small or voyage-3
    raise NotImplementedError("Wire up embedding model in Phase 5")

COLLECTION_MARKET_DATA = "market_data"
COLLECTION_PERSONAS    = "personas"
COLLECTION_BRAND_VOICE = "brand_voice"
VECTOR_SIZE = 1536  # voyage-3 / text-embedding-3-small

async def ensure_collections() -> None:
    qdrant = get_qdrant()
    for name in [COLLECTION_MARKET_DATA, COLLECTION_PERSONAS, COLLECTION_BRAND_VOICE]:
        exists = await qdrant.collection_exists(name)
        if not exists:
            await qdrant.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
```

---

### Phase 1 Exit Criteria
- [ ] All SQLAlchemy models defined
- [ ] Alembic migration runs `alembic upgrade head` without errors
- [ ] `LaunchRepository.create()` + `get()` pass unit tests
- [ ] Redis `SessionStore.set()` / `get()` / `publish()` work against local Redis
- [ ] Qdrant collections created via `ensure_collections()`
- [ ] `src/packages/` types importable from both Python and TypeScript

---

## Phase 2 — API Core

**Goal:** FastAPI app with all middleware, services, and routes returning correct responses. No agent calls yet — services return mock data.

### 2.1 Middleware (`src/apps/api/middleware/`)

**File: `src/apps/api/middleware/security_headers.py`**
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

**File: `src/apps/api/middleware/pii_scrubber.py`**
```python
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Patterns to scrub from request bodies before they reach agents
_EMAIL_RE    = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
_PHONE_RE    = re.compile(r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
_CREDIT_RE   = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

def scrub(text: str) -> str:
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _CREDIT_RE.sub("[CARD]", text)
    return text

class PIIScrubberMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Note: body scrubbing for POST requests requires body buffering
        # Implement per-route if needed; middleware handles headers/query params
        return await call_next(request)
```

**File: `src/apps/api/middleware/rate_limit.py`**
```python
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.memory.short_term.session_store import get_redis

class RateLimitMiddleware(BaseHTTPMiddleware):
    WINDOW = 60       # seconds
    MAX_REQUESTS = 60

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting on health endpoints
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}"
        redis = get_redis()

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.WINDOW)
        count, _ = await pipe.execute()

        if count > self.MAX_REQUESTS:
            return JSONResponse(
                {"error": "rate_limit_exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.WINDOW)},
            )
        return await call_next(request)
```

**File: `src/apps/api/middleware/auth.py`**
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt
from src.apps.api.config import get_settings

settings = get_settings()

# Public routes that skip auth
_PUBLIC_PATHS = {"/api/v1/health", "/api/v1/health/ready", "/docs", "/openapi.json"}

class ClerkAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "unauthorized"}, status_code=401)

        token = auth_header.removeprefix("Bearer ")
        try:
            # Clerk JWTs — verify with Clerk's JWKS endpoint in production
            # For development, decode without verification
            if settings.is_production:
                payload = _verify_clerk_jwt(token)
            else:
                payload = jwt.decode(token, options={"verify_signature": False})
            request.state.user_id = payload.get("sub")
        except Exception:
            return JSONResponse({"error": "invalid_token"}, status_code=401)

        return await call_next(request)

def _verify_clerk_jwt(token: str) -> dict:
    # Fetch JWKS from Clerk and verify
    # Use clerk SDK: from clerk_backend_api import Clerk
    # clerk = Clerk(bearer_auth=settings.clerk_secret_key)
    raise NotImplementedError("Wire up Clerk JWT verification in Phase 8")
```

---

### 2.2 Services (`src/apps/api/services/`)

**File: `src/apps/api/services/launch_service.py`**
```python
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.launch_repo import LaunchRepository
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.apps.api.models.launch import LaunchStatus
from src.packages.config.models import AGENT_MODELS

PIPELINE_AGENTS = [
    "market_intelligence",
    "audience_insight",
    "launch_strategy",
    "content_generation",
]

class LaunchService:
    async def create(self, data: dict[str, Any], user_id: str = "dev") -> dict:
        async with AsyncSessionLocal() as db:
            repo = LaunchRepository(db)
            launch = await repo.create(user_id, data)
            # Pre-create agent run records
            agent_repo = AgentRepository(db)
            for agent_id in PIPELINE_AGENTS:
                await agent_repo.create(launch.launch_id, agent_id)
            return {
                "launch_id": launch.launch_id,
                "status": launch.status,
                "created_at": launch.created_at.isoformat(),
            }

    async def get(self, launch_id: str) -> dict | None:
        async with AsyncSessionLocal() as db:
            repo = LaunchRepository(db)
            launch = await repo.get(launch_id)
            if not launch:
                return None
            agent_repo = AgentRepository(db)
            agents = await agent_repo.get_by_launch(launch_id)
            return {
                "launch_id": launch.launch_id,
                "status": launch.status,
                "brief": launch.brief_output or {},
                "pipeline": [_agent_to_dict(a) for a in agents],
                "hitl_pending": launch.status == LaunchStatus.HITL_PENDING,
                "hitl_checkpoint": None,
            }

    async def run_pipeline(self, launch_id: str) -> None:
        """Called as a background task — invokes the orchestrator."""
        # Phase 3: replace with actual orchestrator invocation
        from src.workers.tasks import run_orchestrator_task
        run_orchestrator_task.delay(launch_id)

def _agent_to_dict(agent) -> dict:
    return {
        "agent_id": agent.agent_id,
        "status": agent.status,
        "output": agent.output,
        "started_at": agent.started_at.isoformat() if agent.started_at else None,
        "completed_at": agent.completed_at.isoformat() if agent.completed_at else None,
    }

def get_launch_service() -> LaunchService:
    return LaunchService()
```

**File: `src/apps/api/services/stream_service.py`**
```python
from __future__ import annotations
import asyncio
import json
from typing import AsyncIterator
from src.memory.short_term.session_store import get_redis

class StreamService:
    """Bridges Redis pub/sub → SSE for the frontend."""

    async def sse_generator(self, launch_id: str) -> AsyncIterator[str]:
        redis = get_redis()
        channel = f"launch:{launch_id}:events"
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            # Send initial connected event
            yield f"data: {json.dumps({'type': 'connected', 'launch_id': launch_id})}\n\n"

            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield f"data: {message['data']}\n\n"
                await asyncio.sleep(0)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

def get_stream_service() -> StreamService:
    return StreamService()
```

**File: `src/apps/api/services/hitl_service.py`**
```python
from __future__ import annotations
from typing import Any
from src.memory.short_term.hitl_state import HITLStateStore
from src.memory.short_term.session_store import SessionStore
import json

class HITLService:
    def __init__(self) -> None:
        self.hitl_store = HITLStateStore()
        self.session_store = SessionStore()

    async def get_pending(self, launch_id: str) -> dict | None:
        return await self.hitl_store.get_pending(launch_id)

    async def resolve(
        self,
        launch_id: str,
        decision: str,
        edits: dict | None,
        comment: str | None,
    ) -> dict | None:
        pending = await self.hitl_store.get_pending(launch_id)
        if not pending:
            return None

        pending["decision"] = decision
        pending["edits"] = edits
        pending["comment"] = comment

        # Publish resume event — the pipeline worker is subscribed to this
        await self.session_store.publish(
            f"launch:{launch_id}:hitl",
            {"type": "hitl_resolved", "decision": decision, "edits": edits},
        )
        await self.hitl_store.clear(launch_id)
        return {"next_step": pending.get("checkpoint")}

def get_hitl_service() -> HITLService:
    return HITLService()
```

**File: `src/apps/api/services/agent_service.py`**
```python
from __future__ import annotations
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository

class AgentService:
    async def get_pipeline_status(self, launch_id: str) -> list[dict] | None:
        async with AsyncSessionLocal() as db:
            repo = AgentRepository(db)
            agents = await repo.get_by_launch(launch_id)
            if not agents:
                return None
            return [
                {
                    "agent_id": a.agent_id,
                    "status": a.status,
                    "output": a.output,
                    "tokens_used": a.tokens_used,
                    "started_at": a.started_at.isoformat() if a.started_at else None,
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                    "error": a.error,
                }
                for a in agents
            ]

    async def retry(self, launch_id: str, agent_id: str) -> bool:
        async with AsyncSessionLocal() as db:
            repo = AgentRepository(db)
            updated = await repo.reset_agent(launch_id, agent_id)
            if not updated:
                return False
            from src.workers.tasks import run_single_agent_task
            run_single_agent_task.delay(launch_id, agent_id)
            return True

def get_agent_service() -> AgentService:
    return AgentService()
```

---

### Phase 2 Exit Criteria
- [ ] `GET /api/v1/health` returns `{"status": "ok"}`
- [ ] `POST /api/v1/launches` creates a DB record + returns `launch_id`
- [ ] `GET /api/v1/launches/{id}` returns launch + pipeline agent statuses
- [ ] `GET /api/v1/launches/{id}/stream` returns `text/event-stream` response
- [ ] `POST /api/v1/hitl/{id}/decide` resolves a pending HITL state
- [ ] Rate limit middleware blocks requests > 60/min
- [ ] Auth middleware returns 401 on missing token
- [ ] All routes have Pydantic request/response models

---

## Phase 3 — Agent Foundation (Orchestrator)

**Goal:** BaseAgent fully operational. Orchestrator drives the full pipeline: dispatches worker agents sequentially, manages HITL pause/resume, synthesizes final brief.

### 3.1 Agent Base (already implemented — verify these files)

- `src/agents/_base/base_agent.py` — `BaseAgent`, `AgentConfig`, `AgentResult`
- `src/agents/_base/cognitive_loop.py` — `run_tool_loop()` (ReAct loop)
- `src/agents/_base/context_builder.py` — `ContextBuilder.inject()`
- `src/agents/_base/output_validator.py` — `OutputValidator.validate()`

### 3.2 Orchestrator System Prompt (`src/agents/orchestrator/prompts/system.md`)

```markdown
You are the LaunchIQ Orchestrator — the central coordinator for product launch intelligence.

Your role:
- Receive a product launch brief from the user
- Plan and dispatch worker agents in sequence
- Inject prior agent outputs as context for downstream agents
- Pause the pipeline at HITL checkpoints for human review
- Synthesize all agent outputs into a final launch brief

Pipeline order:
1. market_intelligence — researches market, competitors, trends
2. audience_insight    — builds personas from market data (depends on #1)
3. launch_strategy     — creates launch plan from market + personas (depends on #1 + #2)
4. content_generation  — writes copy using strategy + brand voice (depends on #3)

HITL checkpoints (pause and wait for human decision before continuing):
- After market_intelligence: "brief_review"
- After launch_strategy: "strategy_review"

Rules:
- Always validate agent outputs against their schemas before proceeding
- If an agent fails, retry once before marking the pipeline failed
- Never fabricate data — only use what agents return
- When pausing for HITL, clearly summarize what was produced and what the human should review
```

### 3.3 Orchestrator Workflow State (`src/agents/orchestrator/workflow_state.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class WorkflowState:
    launch_id: str
    brief: dict[str, Any]
    agent_outputs: dict[str, Any] = field(default_factory=dict)
    current_agent: str | None = None
    hitl_pending: bool = False
    hitl_checkpoint: str | None = None
    completed_agents: list[str] = field(default_factory=list)
    failed: bool = False
    failure_reason: str | None = None

    def mark_agent_complete(self, agent_id: str, output: dict) -> None:
        self.agent_outputs[agent_id] = output
        self.completed_agents.append(agent_id)
        self.current_agent = None

    def mark_hitl_pending(self, checkpoint: str) -> None:
        self.hitl_pending = True
        self.hitl_checkpoint = checkpoint

    def resume_from_hitl(self, edits: dict | None) -> None:
        if edits:
            # Merge edits into the last agent's output
            last_agent = self.completed_agents[-1] if self.completed_agents else None
            if last_agent:
                self.agent_outputs[last_agent].update(edits)
        self.hitl_pending = False
        self.hitl_checkpoint = None
```

### 3.4 Orchestrator Dispatcher (`src/agents/orchestrator/dispatcher.py`)

```python
from __future__ import annotations
import importlib
import asyncio
from typing import Any

AGENT_MODULE_MAP = {
    "market_intelligence": "src.agents.market_intelligence.agent",
    "audience_insight":    "src.agents.audience_insight.agent",
    "launch_strategy":     "src.agents.launch_strategy.agent",
    "content_generation":  "src.agents.content_generation.agent",
    "analytics_feedback":  "src.agents.analytics_feedback.agent",
}

class AgentDispatcher:
    """Instantiates and calls worker agents by name."""

    async def dispatch(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        module_path = AGENT_MODULE_MAP[agent_id]
        module = importlib.import_module(module_path)
        agent_class = getattr(module, f"{_to_class_name(agent_id)}Agent")
        agent = agent_class()
        result = await agent.run(payload)
        return result.output

def _to_class_name(agent_id: str) -> str:
    return "".join(part.capitalize() for part in agent_id.split("_"))
```

### 3.5 Orchestrator Agent (`src/agents/orchestrator/agent.py`)

```python
from __future__ import annotations
import asyncio
import json
from typing import Any, AsyncIterator
from pydantic import BaseModel
from src.agents._base.base_agent import BaseAgent, AgentConfig, AgentResult
from src.packages.config.models import AGENT_MODELS, HITL_CHECKPOINTS
from src.memory.short_term.session_store import SessionStore
from src.memory.short_term.hitl_state import HITLStateStore
from .workflow_state import WorkflowState
from .dispatcher import AgentDispatcher

PIPELINE_SEQUENCE = [
    "market_intelligence",
    "audience_insight",
    "launch_strategy",
    "content_generation",
]

HITL_AFTER = {
    "market_intelligence": "brief_review",
    "launch_strategy":     "strategy_review",
}

class OrchestratorOutput(BaseModel):
    launch_id: str
    status: str
    agent_outputs: dict[str, Any]
    hitl_checkpoint: str | None = None

class OrchestratorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            agent_id="orchestrator",
            model=AGENT_MODELS["orchestrator"],
            enable_thinking=True,
            thinking_budget=8000,
        ))
        self.dispatcher = AgentDispatcher()
        self.session_store = SessionStore()
        self.hitl_store = HITLStateStore()

    def get_output_schema(self) -> type[BaseModel]:
        return OrchestratorOutput

    async def run(self, payload: dict[str, Any]) -> AgentResult:
        launch_id = payload["launch_id"]
        state = WorkflowState(launch_id=launch_id, brief=payload)

        for agent_id in PIPELINE_SEQUENCE:
            state.current_agent = agent_id

            # Publish progress event
            await self._publish_event(launch_id, {"type": "agent_started", "agent_id": agent_id})

            # Build context from prior agent outputs
            agent_payload = {**payload, "prior_outputs": state.agent_outputs}

            try:
                output = await self.dispatcher.dispatch(agent_id, agent_payload)
                state.mark_agent_complete(agent_id, output)
                await self._publish_event(launch_id, {
                    "type": "agent_completed",
                    "agent_id": agent_id,
                    "output": output,
                })
            except Exception as exc:
                await self._publish_event(launch_id, {
                    "type": "agent_failed",
                    "agent_id": agent_id,
                    "error": str(exc),
                })
                state.failed = True
                state.failure_reason = str(exc)
                break

            # HITL checkpoint
            if agent_id in HITL_AFTER:
                checkpoint = HITL_AFTER[agent_id]
                await self._pause_for_hitl(state, checkpoint, output)

                # Wait for HITL resolution (poll Redis)
                decision = await self._wait_for_hitl_resolution(launch_id)
                if decision == "reject":
                    state.failed = True
                    state.failure_reason = "Rejected at HITL checkpoint"
                    break
                edits = decision.get("edits") if isinstance(decision, dict) else None
                state.resume_from_hitl(edits)

        result_output = OrchestratorOutput(
            launch_id=launch_id,
            status="failed" if state.failed else "completed",
            agent_outputs=state.agent_outputs,
            hitl_checkpoint=state.hitl_checkpoint,
        ).model_dump()

        return AgentResult(
            agent_id="orchestrator",
            output=result_output,
            hitl_required=state.hitl_pending,
            hitl_checkpoint=state.hitl_checkpoint,
        )

    async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        # Streaming is handled via Redis pub/sub → SSE
        result = await self.run(payload)
        yield json.dumps(result.output)

    async def _pause_for_hitl(self, state: WorkflowState, checkpoint: str, output: dict) -> None:
        state.mark_hitl_pending(checkpoint)
        await self.hitl_store.set_pending(state.launch_id, {
            "launch_id": state.launch_id,
            "checkpoint": checkpoint,
            "agent_id": state.current_agent or "orchestrator",
            "output_preview": output,
            "created_at": _now(),
        })
        await self._publish_event(state.launch_id, {
            "type": "hitl_required",
            "checkpoint": checkpoint,
            "output_preview": output,
        })

    async def _wait_for_hitl_resolution(self, launch_id: str, timeout: int = 86400) -> dict:
        """Poll Redis for HITL decision. Times out after `timeout` seconds."""
        import time
        start = time.time()
        while time.time() - start < timeout:
            pending = await self.hitl_store.get_pending(launch_id)
            if not pending:
                # Cleared = resolved
                return {"decision": "approve"}
            if pending.get("decision"):
                return pending
            await asyncio.sleep(2)
        return {"decision": "reject"}

    async def _publish_event(self, launch_id: str, event: dict) -> None:
        await self.session_store.publish(f"launch:{launch_id}:events", event)

def _now() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat()
```

### 3.6 Celery Workers (`src/workers/`)

**File: `src/apps/api/workers/celery_app.py`**
```python
from celery import Celery
from src.apps.api.config import get_settings

settings = get_settings()

celery_app = Celery(
    "launchiq",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.apps.api.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
```

**File: `src/apps/api/workers/tasks.py`**
```python
import asyncio
from src.apps.api.workers.celery_app import celery_app

@celery_app.task(name="run_orchestrator", bind=True, max_retries=1)
def run_orchestrator_task(self, launch_id: str) -> None:
    from src.agents.orchestrator.agent import OrchestratorAgent
    agent = OrchestratorAgent()
    payload = _load_brief(launch_id)
    asyncio.run(agent.run(payload))

@celery_app.task(name="run_single_agent", bind=True, max_retries=2)
def run_single_agent_task(self, launch_id: str, agent_id: str) -> None:
    from src.agents.orchestrator.dispatcher import AgentDispatcher
    dispatcher = AgentDispatcher()
    payload = _load_brief(launch_id)
    asyncio.run(dispatcher.dispatch(agent_id, payload))

def _load_brief(launch_id: str) -> dict:
    from src.memory.structured.database import AsyncSessionLocal
    from src.memory.structured.repositories.launch_repo import LaunchRepository
    async def _get():
        async with AsyncSessionLocal() as db:
            repo = LaunchRepository(db)
            launch = await repo.get(launch_id)
            return {
                "launch_id": launch.launch_id,
                "product_name": launch.product_name,
                "description": launch.description,
                "target_market": launch.target_market,
                "competitors": launch.competitors,
            }
    return asyncio.run(_get())
```

### Phase 3 Exit Criteria
- [ ] `OrchestratorAgent.run()` completes end-to-end with mock worker agents (stubs that return empty dicts)
- [ ] HITL pause publishes event to Redis; resume from HITL continues pipeline
- [ ] Celery worker picks up `run_orchestrator` task and calls `OrchestratorAgent`
- [ ] Progress events published to `launch:{id}:events` channel
- [ ] `WorkflowState` correctly tracks completed agents and prior outputs

---

## Phase 4 — Worker Agents

**Goal:** All 5 worker agents implemented with real Claude calls, tool use, schemas, and system prompts.

### Pattern (apply to all agents):

Each agent follows this structure:
```
agent_id/
├── agent.py          # Inherits BaseAgent, implements run() + stream() + get_output_schema()
├── schemas.py        # Pydantic output schema (enforced by OutputValidator)
├── prompts/
│   └── system.md     # System prompt (loaded at agent init)
├── handler.py        # Lambda handler — wraps agent.run() for AWS Lambda
└── tests/
    └── test_agent.py # Unit tests with mocked Anthropic client
```

---

### 4.1 Market Intelligence Agent

**File: `src/agents/market_intelligence/schemas.py`**
```python
from pydantic import BaseModel, Field

class Competitor(BaseModel):
    name: str
    positioning: str
    strengths: list[str]
    weaknesses: list[str]
    pricing: str | None = None

class MarketTrend(BaseModel):
    trend: str
    relevance: str
    source: str | None = None

class MarketIntelligenceOutput(BaseModel):
    market_size: str
    growth_rate: str
    competitors: list[Competitor] = Field(min_length=1, max_length=10)
    trends: list[MarketTrend] = Field(min_length=1, max_length=10)
    white_space: str
    recommended_positioning: str
```

**File: `src/agents/market_intelligence/prompts/system.md`**
```markdown
You are the Market Intelligence Agent for LaunchIQ. You research markets with precision.

Your task:
1. Use the tavily_search tool to research the target market and competitors
2. Identify market size, growth rate, key trends
3. Analyze each competitor: positioning, strengths, weaknesses, pricing
4. Identify white space opportunities
5. Recommend a differentiated positioning

Rules:
- Search for at minimum 3 competitors
- Always include the source/evidence for market size claims
- Never fabricate statistics — use the search results
- Return a structured JSON matching MarketIntelligenceOutput schema
```

**File: `src/agents/market_intelligence/agent.py`**
```python
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, AsyncIterator
from pydantic import BaseModel
from src.agents._base.base_agent import BaseAgent, AgentConfig, AgentResult
from src.packages.config.models import AGENT_MODELS
from .schemas import MarketIntelligenceOutput

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system.md").read_text()

# MCP tool definition for Tavily search
_TAVILY_TOOL = {
    "name": "tavily_search",
    "description": "Search the web for market research, competitor analysis, and industry trends",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
}

class MarketIntelligenceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            agent_id="market_intelligence",
            model=AGENT_MODELS["market_intelligence"],
            system_prompt=_SYSTEM_PROMPT,
            tools=[_TAVILY_TOOL],
            max_tokens=4096,
        ))

    def get_output_schema(self) -> type[BaseModel]:
        return MarketIntelligenceOutput

    async def run(self, payload: dict[str, Any]) -> AgentResult:
        from src.tools.tavily_search.tools import TavilySearchExecutor
        tool_executor = TavilySearchExecutor()

        user_msg = (
            f"Research the market for: {payload['product_name']}\n"
            f"Description: {payload['description']}\n"
            f"Target market: {payload['target_market']}\n"
            f"Known competitors: {', '.join(payload.get('competitors', []))}"
        )
        messages = self._build_messages(user_msg)
        final_text, tool_log, thinking = await self._call_with_tools(messages, tool_executor)

        # Parse JSON from final text
        output_dict = _extract_json(final_text)
        validated = self._validate_output(output_dict)

        return AgentResult(
            agent_id="market_intelligence",
            output=validated,
            thinking=thinking,
            tool_calls=tool_log,
        )

    async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        result = await self.run(payload)
        yield json.dumps(result.output)

def _extract_json(text: str) -> dict:
    """Extract JSON block from Claude's response text."""
    import re
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Try raw JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"No JSON found in agent response: {text[:200]}")
```

**File: `src/agents/market_intelligence/handler.py`**
```python
"""AWS Lambda handler for market_intelligence agent."""
import json
import asyncio
from .agent import MarketIntelligenceAgent

def handler(event: dict, context) -> dict:
    """Lambda entry point."""
    payload = event.get("payload", event)
    agent = MarketIntelligenceAgent()
    result = asyncio.run(agent.run(payload))
    return {
        "statusCode": 200,
        "body": json.dumps(result.output),
    }
```

---

### 4.2 Audience Insight Agent

**File: `src/agents/audience_insight/schemas.py`**
```python
from pydantic import BaseModel, Field

class Persona(BaseModel):
    name: str
    role: str
    age_range: str
    pain_points: list[str] = Field(min_length=2, max_length=5)
    goals: list[str] = Field(min_length=2, max_length=5)
    channels: list[str]
    message_hook: str
    willingness_to_pay: str

class AudienceInsightOutput(BaseModel):
    primary_persona: Persona
    secondary_personas: list[Persona] = Field(max_length=3)
    icp_summary: str
    messaging_framework: dict[str, str]  # {segment: core_message}
    recommended_channels: list[str]
```

**File: `src/agents/audience_insight/prompts/system.md`**
```markdown
You are the Audience Insight Agent for LaunchIQ. You build precise buyer personas.

Your task:
1. Analyze the market intelligence data provided in context
2. Define 1 primary and 1-3 secondary buyer personas
3. For each persona: name, role, age range, pain points, goals, channels, message hook
4. Build a messaging framework: one core message per segment
5. Recommend top 3 channels to reach each persona

Rules:
- Base personas on the market data — not generic templates
- Pain points must be specific to this product's market
- Each persona's message_hook should be ≤ 15 words
- Return valid JSON matching AudienceInsightOutput schema
```

**Implementation:** Same pattern as MarketIntelligenceAgent. No external tool calls needed — context comes from prior agent outputs. Call `client.messages.create()` directly (no tool executor).

---

### 4.3 Launch Strategy Agent

**File: `src/agents/launch_strategy/schemas.py`**
```python
from pydantic import BaseModel, Field

class LaunchPhase(BaseModel):
    phase: str            # "Pre-Launch" | "Launch Week" | "Post-Launch"
    duration: str
    goals: list[str]
    tactics: list[str] = Field(min_length=3)
    kpis: list[str]

class LaunchStrategyOutput(BaseModel):
    positioning_statement: str
    launch_date_recommendation: str
    phases: list[LaunchPhase] = Field(min_length=3, max_length=4)
    channels: list[str]
    budget_allocation: dict[str, str]  # {channel: percentage}
    success_metrics: list[str]
    risks: list[str]
```

**Note:** Enable extended thinking (`enable_thinking=True`) for this agent — strategy requires deeper reasoning. Use `claude-opus-4-6`.

---

### 4.4 Content Generation Agent

**File: `src/agents/content_generation/schemas.py`**
```python
from pydantic import BaseModel, Field

class ContentItem(BaseModel):
    format: str         # "email" | "linkedin" | "twitter" | "ad_copy" | "landing_page"
    variant: str        # "a" | "b" for A/B variants
    headline: str
    body: str
    cta: str
    target_persona: str

class ContentBundle(BaseModel):
    email_sequence: list[ContentItem] = Field(min_length=3, max_length=5)
    social_posts: list[ContentItem] = Field(min_length=3, max_length=10)
    ad_copy: list[ContentItem] = Field(min_length=2, max_length=4)
    brand_voice_notes: str
```

**Note:** Use parallelization pattern — generate email, social, and ad copy in parallel using `asyncio.gather()`. Uses `claude-sonnet-4-6`.

---

### 4.5 Analytics & Feedback Agent

**File: `src/agents/analytics_feedback/schemas.py`**
```python
from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    area: str
    insight: str
    action: str
    priority: str  # "high" | "medium" | "low"

class AnalyticsOutput(BaseModel):
    engagement_score: float = Field(ge=0.0, le=1.0)
    top_performing_content: list[str]
    underperforming_content: list[str]
    recommendations: list[Recommendation] = Field(min_length=3)
    predicted_next_action: str
```

**Note:** Uses GA4 MCP tool for real analytics data. Uses `claude-haiku-4-5-20251001` (cost optimization).

---

### 4.6 Lambda Handlers (all agents)

All agents follow the same Lambda handler pattern (see `market_intelligence/handler.py` above). Wire to AWS Lambda via `src/infra/aws/stacks/agents_stack.py`.

### Phase 4 Exit Criteria
- [ ] All 5 worker agents have complete `agent.py`, `schemas.py`, `prompts/system.md`, `handler.py`
- [ ] Each agent's `run()` makes a real Anthropic API call (integration test, mocked in unit tests)
- [ ] `OutputValidator` rejects outputs that don't match schemas
- [ ] `OrchestratorAgent` calls all 4 pipeline agents end-to-end
- [ ] Full pipeline E2E test: brief input → `analytics_feedback` output

---

## Phase 5 — MCP Tool Servers

**Goal:** All 5 MCP tool servers working. Agents call real external APIs.

### 5.1 Tool Server Pattern

Each tool server follows this structure:
```
tools/
└── tool_name/
    ├── server.py    # FastMCP server definition
    ├── tools.py     # Tool executor (called by cognitive loop)
    ├── schemas.py   # Input/output Pydantic schemas
    └── auth.py      # API key / OAuth helpers
```

### 5.2 Tavily Search (`src/tools/tavily_search/`)

**File: `src/tools/tavily_search/tools.py`**
```python
from __future__ import annotations
import httpx
from src.apps.api.config import get_settings

settings = get_settings()

class TavilySearchExecutor:
    BASE_URL = "https://api.tavily.com/search"

    async def execute(self, tool_name: str, inputs: dict) -> dict:
        if tool_name != "tavily_search":
            raise ValueError(f"Unknown tool: {tool_name}")
        return await self._search(inputs["query"], inputs.get("max_results", 5))

    async def _search(self, query: str, max_results: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.BASE_URL,
                json={
                    "api_key": settings.tavily_api_key,  # add to Settings
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "advanced",
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
```

### 5.3 Internal Tool Server (`src/tools/internal/`)

Provides agents access to LaunchIQ's own data:

```python
# tools/internal/tools.py
class InternalToolExecutor:
    """Allows agents to read/write launch data within the session."""

    async def execute(self, tool_name: str, inputs: dict) -> dict:
        match tool_name:
            case "get_prior_output":
                return await self._get_prior_output(inputs["launch_id"], inputs["agent_id"])
            case "save_output":
                return await self._save_output(inputs["launch_id"], inputs["agent_id"], inputs["output"])
            case _:
                raise ValueError(f"Unknown internal tool: {tool_name}")
```

### 5.4 HubSpot, Slack, GA4 Servers

Follow the same `TavilySearchExecutor` pattern. Use official SDKs:
- HubSpot: `hubspot-api-client`
- Slack: `slack-sdk`
- GA4: `google-analytics-data`

Each wraps API calls behind the `execute(tool_name, inputs)` interface so the cognitive loop stays tool-agnostic.

### Phase 5 Exit Criteria
- [ ] `TavilySearchExecutor` returns real search results for a test query
- [ ] `InternalToolExecutor` reads/writes agent outputs to Redis session store
- [ ] HubSpot tool can create a contact
- [ ] Slack tool can post a message to a channel
- [ ] GA4 tool can fetch session metrics for a property
- [ ] All tools have Pydantic input validation (no raw dict passing to external APIs)

---

## Phase 6 — Frontend

**Goal:** Next.js 15 app with working intake form, real-time agent pipeline view (SSE), HITL decision UI.

### 6.1 Shared Types (`src/packages/types/index.ts`)
```typescript
// Re-export everything
export * from './launch';
export * from './agent';
export * from './hitl';
```

### 6.2 API Client (`src/apps/web/lib/api.ts`)
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function createLaunch(data: {
  product_name: string;
  description: string;
  target_market: string;
  competitors: string[];
}): Promise<{ launch_id: string; status: string }> {
  const res = await fetch(`${BASE_URL}/api/v1/launches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getLaunch(launchId: string) {
  const res = await fetch(`${BASE_URL}/api/v1/launches/${launchId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function resolveHITL(
  launchId: string,
  decision: 'approve' | 'edit' | 'reject',
  edits?: Record<string, unknown>
) {
  const res = await fetch(`${BASE_URL}/api/v1/hitl/${launchId}/decide`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision, edits }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

### 6.3 SSE Hook (`src/apps/web/lib/sse.ts`)
```typescript
import { useEffect, useRef, useCallback } from 'react';

export function useSSE(launchId: string | null, onEvent: (event: unknown) => void) {
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!launchId) return;
    const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/launches/${launchId}/stream`;
    esRef.current = new EventSource(url);

    esRef.current.onmessage = (e) => {
      try { onEvent(JSON.parse(e.data)); } catch {}
    };

    esRef.current.onerror = () => esRef.current?.close();

    return () => { esRef.current?.close(); };
  }, [launchId, onEvent]);
}
```

### 6.4 Zustand Store (`src/apps/web/store/launchStore.ts`)
```typescript
import { create } from 'zustand';
import type { Launch, AgentRun, HITLState } from '@/packages/types';

interface LaunchStore {
  launch: Launch | null;
  agents: AgentRun[];
  hitl: HITLState | null;
  setLaunch: (l: Launch) => void;
  updateAgent: (agent: AgentRun) => void;
  setHITL: (h: HITLState | null) => void;
}

export const useLaunchStore = create<LaunchStore>((set) => ({
  launch: null,
  agents: [],
  hitl: null,
  setLaunch: (launch) => set({ launch }),
  updateAgent: (agent) =>
    set((s) => ({
      agents: s.agents.some((a) => a.agent_id === agent.agent_id)
        ? s.agents.map((a) => (a.agent_id === agent.agent_id ? agent : a))
        : [...s.agents, agent],
    })),
  setHITL: (hitl) => set({ hitl }),
}));
```

### 6.5 Key Components

**`IntakeForm.tsx`** — Form with fields: product_name, description, target_market, competitors (tag input). On submit → `createLaunch()` → redirect to `/launch/[id]/tracker`.

**`AgentPipeline.tsx`** — Renders 4 `AgentCard` components in sequence. Each card shows: agent name, status badge (pending/running/completed/failed), token count, output preview on hover.

**`AgentCard.tsx`** — Single agent status card. Shows animated spinner when `status === 'running'`. Uses SSE events to update via `useLaunchStore`.

**`HITLCheckpoint.tsx`** — Full-page overlay when `hitl_pending === true`. Shows agent output preview. Contains `HITLDecisionBar` (approve/edit/reject buttons).

**`HITLDecisionBar.tsx`** — Three buttons: Approve (green), Edit (yellow), Reject (red). Edit opens `HITLEditModal`.

**`HITLEditModal.tsx`** — JSON editor for modifying agent output before approving. Uses `@uiw/react-json-view` or similar.

### 6.6 Pages

**`app/(app)/launch/new/page.tsx`** — Renders `IntakeForm`. On submit → redirect to tracker.

**`app/(app)/launch/[id]/tracker/page.tsx`**
```tsx
// Key logic:
// 1. Fetch launch on mount
// 2. Subscribe to SSE stream
// 3. On each event: update useLaunchStore
// 4. If hitl_pending: show HITLCheckpoint overlay
// 5. Show AgentPipeline throughout
```

### Phase 6 Exit Criteria
- [ ] Intake form submits and navigates to tracker
- [ ] Tracker page shows 4 agent cards with live status updates via SSE
- [ ] HITL overlay appears when `hitl_pending === true`
- [ ] Approve/Edit/Reject buttons call `/api/v1/hitl/{id}/decide`
- [ ] Dashboard shows list of launches with status
- [ ] App builds without TypeScript errors (`pnpm typecheck`)
- [ ] `pnpm lint` passes

---

## Phase 7 — Eval Framework

**Goal:** Per-agent eval suites with baseline comparison. CI eval gate blocks PRs that regress.

### 7.1 Evaluator Core (`src/evals/framework/evaluator.py`)

```python
from __future__ import annotations
from typing import Any
from .scorer import Scorer
from .langfuse_client import LangfuseClient
from .reporter import Reporter

class Evaluator:
    def __init__(self) -> None:
        self.scorer = Scorer()
        self.langfuse = LangfuseClient()
        self.reporter = Reporter()

    async def run_suite(self, agent_id: str, test_cases: list[dict], expected: list[dict]) -> dict:
        results = []
        for case, expected_output in zip(test_cases, expected):
            actual = await self._run_agent(agent_id, case["input"])
            scores = self.scorer.score(actual, expected_output)
            results.append({"input": case, "actual": actual, "scores": scores})
            self.langfuse.log(agent_id, case, actual, scores)

        summary = self.reporter.summarize(agent_id, results)
        return summary

    async def _run_agent(self, agent_id: str, inputs: dict) -> dict:
        from src.agents.orchestrator.dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        return await dispatcher.dispatch(agent_id, inputs)
```

### 7.2 Scorer (`src/evals/metrics/`)

```python
# relevance.py  — cosine similarity of output vs expected (via embeddings)
# hallucination.py — checks for phrases not grounded in context
# schema_compliance.py — validates output against agent's Pydantic schema
# edit_rate.py — measures how often HITL humans edited the output (lower = better)
```

### 7.3 Baseline (`src/evals/regression/baseline.json`)

```json
{
  "market_intelligence": {
    "relevance_score":    0.82,
    "hallucination_rate": 0.03,
    "schema_compliance":  1.00
  },
  "audience_insight": {
    "relevance_score":    0.80,
    "hallucination_rate": 0.02,
    "schema_compliance":  1.00
  },
  "launch_strategy": {
    "relevance_score":    0.85,
    "hallucination_rate": 0.04,
    "schema_compliance":  1.00
  },
  "content_generation": {
    "relevance_score":    0.78,
    "hallucination_rate": 0.05,
    "schema_compliance":  1.00
  }
}
```

### 7.4 Regression Runner (`src/evals/regression/run_regression.py`)

```python
#!/usr/bin/env python3
"""
Run eval suites against all agents and compare against baseline.
Usage:
  python run_regression.py            # run and report
  python run_regression.py --assert-baseline  # fail if below baseline
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

BASELINE = json.loads((Path(__file__).parent / "baseline.json").read_text())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-baseline", action="store_true")
    args = parser.parse_args()

    results = asyncio.run(run_all_suites())
    print(json.dumps(results, indent=2))

    if args.assert_baseline:
        failed = check_baseline(results, BASELINE)
        if failed:
            print(f"\nEVAL GATE FAILED: {failed}", file=sys.stderr)
            sys.exit(1)
        print("\nEval gate passed.")

async def run_all_suites() -> dict:
    from src.evals.framework.evaluator import Evaluator
    evaluator = Evaluator()
    results = {}
    for agent_id in ["market_intelligence", "audience_insight", "launch_strategy", "content_generation"]:
        suite_path = Path(f"src/evals/suites/{agent_id}")
        test_cases = json.loads((suite_path / "test_cases.json").read_text())
        expected = json.loads((suite_path / "expected_outputs.json").read_text())
        results[agent_id] = await evaluator.run_suite(agent_id, test_cases, expected)
    return results

def check_baseline(results: dict, baseline: dict) -> list[str]:
    failures = []
    for agent_id, metrics in baseline.items():
        actual = results.get(agent_id, {})
        for metric, threshold in metrics.items():
            actual_val = actual.get(metric, 0)
            if metric == "hallucination_rate":
                if actual_val > threshold:
                    failures.append(f"{agent_id}.{metric}: {actual_val} > {threshold}")
            else:
                if actual_val < threshold:
                    failures.append(f"{agent_id}.{metric}: {actual_val} < {threshold}")
    return failures

if __name__ == "__main__":
    main()
```

### Phase 7 Exit Criteria
- [ ] `python run_regression.py` runs all 4 agent suites
- [ ] `--assert-baseline` exits 0 when scores meet baseline, exits 1 when they don't
- [ ] `pr.yml` eval-gate step runs and blocks on failure
- [ ] Langfuse receives trace data per eval run
- [ ] `update_baseline.py` updates `baseline.json` after intentional improvements

---

## Phase 8 — Infrastructure

**Goal:** AWS CDK stacks deployable. Dockerfiles build. CI/CD pipelines complete.

### 8.1 AWS CDK Stacks (`src/infra/aws/stacks/`)

**`agents_stack.py`** — Creates one Lambda function per agent:
```python
from aws_cdk import Stack, Duration
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

class AgentsStack(Stack):
    AGENTS = [
        "market_intelligence",
        "audience_insight",
        "launch_strategy",
        "content_generation",
        "analytics_feedback",
    ]

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        for agent_id in self.AGENTS:
            lambda_.Function(
                self, f"Agent-{agent_id}",
                function_name=f"launchiq-{agent_id}",
                runtime=lambda_.Runtime.PYTHON_3_12,
                handler=f"src.agents.{agent_id}.handler.handler",
                code=lambda_.Code.from_asset("src/agents"),
                timeout=Duration.seconds(300),
                memory_size=1024,
                environment={
                    "ANTHROPIC_API_KEY": "{{resolve:secretsmanager:launchiq/anthropic}}",
                },
            )
```

**`api_stack.py`** — ECS Fargate service for FastAPI.

**`data_stack.py`** — RDS PostgreSQL, ElastiCache Redis, Qdrant on EC2.

**`secrets_stack.py`** — AWS Secrets Manager entries for all API keys.

### 8.2 Dockerfiles

**`src/infra/docker/api.Dockerfile`**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY src/apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`src/infra/docker/worker.Dockerfile`**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY src/apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["celery", "-A", "src.apps.api.workers.celery_app.celery_app", "worker", "--loglevel=info"]
```

### 8.3 Complete CI/CD Workflows

**`deploy-staging.yml`** — Same structure as `deploy-production.yml` but:
- Triggered on push to `dev` branch
- Deploys to `launchiq-staging` ECS cluster
- No smoke test Slack notification
- Tags image as `:staging`

**`eval-scheduled.yml`** — Weekly cron:
```yaml
name: Scheduled Eval
on:
  schedule:
    - cron: '0 9 * * 1'   # Every Monday 9am UTC
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r src/apps/api/requirements.txt
      - name: Run full eval suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
          LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
        run: |
          python src/evals/regression/run_regression.py
          python src/evals/regression/update_baseline.py --if-improved
```

### Phase 8 Exit Criteria
- [ ] `cdk synth` completes without errors (outputs CloudFormation templates)
- [ ] `docker build -f src/infra/docker/api.Dockerfile .` succeeds
- [ ] `docker-compose up -d` starts Postgres + Redis + Qdrant locally
- [ ] `pr.yml` runs on every PR: lint + typecheck + tests + eval gate
- [ ] `deploy-staging.yml` deploys on push to `dev`
- [ ] `deploy-production.yml` deploys on semver tag push

---

## Phase 9 — Integration & Polish

**Goal:** Full E2E demo flow working. Repo ready to present to hiring managers and investors.

### 9.1 Demo Data

Create `src/data/demo/` with realistic seed data:
- `demo_launch.json` — LaunchIQ's own launch brief (dogfood the product)
- `demo_market_output.json` — Pre-computed market intelligence output
- `demo_personas.json` — 2 realistic buyer personas

Load via: `python src/data/seed.py --demo`

### 9.2 Local Development Script

Create `Makefile`:
```makefile
dev:
    docker-compose up -d
    pnpm install
    cd src/apps/web && pnpm dev &
    uvicorn src.apps.api.main:app --reload --port 8000 &
    celery -A src.apps.api.workers.celery_app.celery_app worker --loglevel=info

test:
    pytest src/ --cov=src --cov-report=term-missing

eval:
    python src/evals/regression/run_regression.py

migrate:
    cd src/memory/structured && alembic upgrade head

seed:
    python src/data/seed.py --demo
```

### 9.3 Final Checklist

- [ ] `README.md` badges link to real CI status
- [ ] `.env.example` has all required keys documented
- [ ] Full E2E demo: submit brief → watch 4 agents run → HITL approve → view content
- [ ] At least one real Anthropic API call tested (not all mocked)
- [ ] `pnpm build` completes for Next.js frontend
- [ ] `pytest src/ -x` passes all unit tests
- [ ] `python run_regression.py --assert-baseline` passes
- [ ] Deployed to staging URL for live demo

---

## Copilot Usage Tips

### Context to always include when prompting Copilot:
1. The file you're implementing (open it in editor)
2. The phase section from this document
3. The related schemas (`schemas.py`) and tests (`test_agent.py`)

### Prompt patterns that work well:
- *"Implement `AudienceInsightAgent.run()` following the same pattern as `MarketIntelligenceAgent.run()` in `src/agents/market_intelligence/agent.py`. The output schema is in `schemas.py`. No tool calls needed — context comes from `prior_outputs`."*
- *"Write unit tests for `LaunchRepository` in `test_launch_repo.py`. Mock `AsyncSession`. Test `create()` and `get()`. Use pytest-asyncio."*
- *"Implement `HITLCheckpoint.tsx` — it should render a full-page overlay when `hitl !== null` from `useLaunchStore`. Include `HITLDecisionBar` with approve/edit/reject. Call `resolveHITL()` from `lib/api.ts` on decision."*

### Never ask Copilot to:
- Design architecture (it's already designed here)
- Choose models (set in `src/packages/config/models.py`)
- Decide on schema fields (defined in each agent's `schemas.py`)
- Write CI/CD workflows from scratch (they're in `.github/workflows/`)
