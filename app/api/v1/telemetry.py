"""
app/api/v1/telemetry.py — Telemetry events and observability query endpoints.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, require_permission
from app.db.session import get_db
from app.db.models import AuditLog, TokenUsage, BenchmarkBaseline

router = APIRouter(prefix="/v1/telemetry", tags=["telemetry"])


@router.get("/events")
async def list_audit_events(
    user: Annotated[CurrentUser, Depends(require_permission("telemetry:read"))],
    db: AsyncSession = Depends(get_db),
    run_id: str | None = Query(None),
    actor: str | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """Query audit log events with optional filters."""
    q = select(AuditLog).order_by(AuditLog.occurred_at.desc()).limit(limit)
    if user.org_id:
        q = q.where(AuditLog.org_id == user.org_id)
    if run_id:
        q = q.where(AuditLog.run_id == run_id)
    if actor:
        q = q.where(AuditLog.actor.contains(actor))
    if action:
        q = q.where(AuditLog.action == action)

    result = await db.execute(q)
    events = result.scalars().all()
    return [
        {
            "id": e.id,
            "actor": e.actor,
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "outcome": e.outcome,
            "risk_level": e.risk_level,
            "run_id": e.run_id,
            "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
        }
        for e in events
    ]


@router.get("/token-usage")
async def token_usage(
    user: Annotated[CurrentUser, Depends(require_permission("telemetry:read"))],
    db: AsyncSession = Depends(get_db),
    skill_name: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Query token usage records."""
    q = select(TokenUsage).order_by(TokenUsage.recorded_at.desc()).limit(limit)
    if user.org_id:
        q = q.where(TokenUsage.org_id == user.org_id)
    if skill_name:
        q = q.where(TokenUsage.skill_name == skill_name)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "skill_name": r.skill_name,
            "model": r.model,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "estimated_cost_usd": r.estimated_cost_usd,
            "run_id": r.run_id,
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
        }
        for r in rows
    ]


@router.get("/benchmarks")
async def skill_benchmarks(
    user: Annotated[CurrentUser, Depends(require_permission("telemetry:read"))],
    db: AsyncSession = Depends(get_db),
    skill_name: str | None = Query(None),
):
    """Retrieve benchmark baselines for skills."""
    q = select(BenchmarkBaseline).order_by(BenchmarkBaseline.computed_at.desc())
    if skill_name:
        q = q.where(BenchmarkBaseline.skill_name == skill_name)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "skill_name": r.skill_name,
            "p50_latency_ms": r.p50_latency_ms,
            "p95_latency_ms": r.p95_latency_ms,
            "p99_latency_ms": r.p99_latency_ms,
            "avg_input_tokens": r.avg_input_tokens,
            "avg_output_tokens": r.avg_output_tokens,
            "success_rate": r.success_rate,
            "window_runs": r.window_runs,
            "computed_at": r.computed_at.isoformat() if r.computed_at else None,
        }
        for r in rows
    ]