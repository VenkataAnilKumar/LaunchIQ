"""Application configuration — loaded once at startup from environment."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "LaunchIQ API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Auth (Clerk)
    clerk_publishable_key: str = ""
    clerk_secret_key: str = ""
    clerk_jwt_audience: str = ""
    integration_encryption_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/launchiq"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # Tavily
    tavily_api_key: str = ""

    # OpenAI (embeddings via text-embedding-3-small)
    openai_api_key: str = ""

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    sentry_dsn: str = ""

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
