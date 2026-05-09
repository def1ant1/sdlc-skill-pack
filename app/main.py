"""
app/main.py — FastAPI application factory for Apotheon SDLC Skills API.

Lifespan:
  startup  → init_db(), setup_tracing(), register built-in connectors
  shutdown → flush OTel spans

Routers registered:
  /v1/workflows     — workflow CRUD + execution
  /v1/approvals     — HITL approval queue
  /v1/memory        — semantic memory search
  /v1/connectors    — connector registry + health
  /v1/telemetry     — audit events, token usage, benchmarks
  /v1/governance    — policy management, dashboard
  /v1/cost          — cost estimation
  /metrics          — Prometheus scrape endpoint
  /health           — liveness probe
  /ws/runs/{run_id} — WebSocket live updates (optional)
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse

logger = logging.getLogger("apotheon.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    from app.db.session import init_db
    await init_db()

    from app.observability.tracing import setup_tracing
    setup_tracing(
        service_name=os.environ.get("OTEL_SERVICE_NAME", "apotheon"),
        otlp_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", ""),
    )

    logger.info("Apotheon API started")
    yield

    # --- Shutdown ---
    from app.observability.tracing import _provider
    if _provider:
        try:
            _provider.shutdown()
        except Exception:
            pass
    logger.info("Apotheon API shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Apotheon SDLC Skills API",
        description="AI-powered SDLC orchestration platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    origins = os.environ.get("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Tenant isolation middleware
    from app.middleware.tenant import TenantMiddleware
    app.add_middleware(TenantMiddleware)

    # --- API Routers ---
    from app.api.v1.workflows import router as workflows_router
    from app.api.v1.approvals import router as approvals_router
    from app.api.v1.memory import router as memory_router
    from app.api.v1.connectors import router as connectors_router
    from app.api.v1.telemetry import router as telemetry_router
    from app.api.v1.governance import router as governance_router
    from app.api.v1.cost import router as cost_router

    app.include_router(workflows_router)
    app.include_router(approvals_router)
    app.include_router(memory_router)
    app.include_router(connectors_router)
    app.include_router(telemetry_router)
    app.include_router(governance_router)
    app.include_router(cost_router)

    # --- Prometheus metrics ---
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        from app.observability.metrics import get_metrics_response
        content, content_type = get_metrics_response()
        return PlainTextResponse(content=content, media_type=content_type)

    # --- Liveness / readiness ---
    @app.get("/health", include_in_schema=False)
    async def health():
        return JSONResponse({"status": "ok", "service": "apotheon"})

    @app.get("/ready", include_in_schema=False)
    async def ready():
        # Check DB connectivity
        try:
            from app.db.session import get_db
            from sqlalchemy import text
            async for db in get_db():
                await db.execute(text("SELECT 1"))
                break
            db_ok = True
        except Exception:
            db_ok = False

        status = "ok" if db_ok else "degraded"
        code = 200 if db_ok else 503
        return JSONResponse({"status": status, "db": db_ok}, status_code=code)

    return app


app = create_app()