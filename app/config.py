"""
app/config.py — Application settings via Pydantic BaseSettings.

All values can be overridden by environment variables (case-insensitive).
"""
from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    # Database — SQLite for dev, Postgres for prod
    database_url: str = os.environ.get(
        "DATABASE_URL", "sqlite+aiosqlite:///./apotheon.db"
    )
    database_url_sync: str = os.environ.get(
        "DATABASE_URL_SYNC", "sqlite:///./apotheon.db"
    )

    # Redis
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Qdrant
    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")

    # JWT
    jwt_secret: str = os.environ.get("JWT_SECRET", "change-me-in-production-use-32-chars")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

    # Anthropic
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    # Temporal
    temporal_host: str = os.environ.get("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace: str = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
    temporal_task_queue: str = os.environ.get("TEMPORAL_TASK_QUEUE", "apotheon-sdlc")

    # Platform
    execution_mode: str = os.environ.get("EXECUTION_MODE", "local")
    embedding_backend: str = os.environ.get("EMBEDDING_BACKEND", "ollama")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")

    # Vault
    vault_addr: str = os.environ.get("VAULT_ADDR", "http://localhost:8200")
    vault_token: str = os.environ.get("VAULT_TOKEN", "")
    vault_secret_path_prefix: str = os.environ.get(
        "VAULT_SECRET_PATH_PREFIX", "secret/connectors"
    )

    # Rate limiting
    rate_limit_per_minute: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "100"))
    rate_limit_workflows_per_hour: int = int(
        os.environ.get("RATE_LIMIT_WORKFLOWS_PER_HOUR", "60")
    )

    # Feature flags
    enable_knowledge_graph: bool = os.environ.get("ENABLE_KNOWLEDGE_GRAPH", "false").lower() == "true"
    enable_billing: bool = os.environ.get("ENABLE_BILLING", "false").lower() == "true"
    enable_multitenancy: bool = os.environ.get("ENABLE_MULTITENANCY", "false").lower() == "true"

    # Telemetry
    telemetry_log: str = os.environ.get("TELEMETRY_LOG", "telemetry.log.yaml")
    otel_endpoint: str = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()