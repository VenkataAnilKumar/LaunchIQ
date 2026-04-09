"""FastAPI application entry point."""
from __future__ import annotations

import logging

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .middleware.auth import ClerkAuthMiddleware
from .middleware.pii_scrubber import PIIScrubberMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .routers import agents, health, hitl, integrations, launches

settings = get_settings()

# Sentry — errors only in production
if settings.sentry_dsn and settings.is_production:
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

# ------------------------------------------------------------------ #
# Middleware (applied in reverse order — last added = outermost)      #
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://launchiq.io", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(PIIScrubberMiddleware)
app.add_middleware(ClerkAuthMiddleware)

# ------------------------------------------------------------------ #
# Routers                                                              #
# ------------------------------------------------------------------ #
app.include_router(health.router, tags=["health"])
app.include_router(launches.router, prefix="/api/v1/launches", tags=["launches"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(hitl.router, prefix="/api/v1/hitl", tags=["hitl"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])


@app.on_event("startup")
async def startup() -> None:
    logger.info("LaunchIQ API starting — env=%s", settings.environment)


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("LaunchIQ API shutting down")
