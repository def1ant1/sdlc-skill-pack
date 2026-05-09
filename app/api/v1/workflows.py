"""
app/api/v1/workflows.py — Workflow submission, status, and step log endpoints.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, require_permission
from app.db.session import get_db
from app.db.repositories.workflow_repository import WorkflowRepository
from app.db.repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

# Inject runtime path so execute_workflow is importable
_RUNTIME = str(Path(__file__).parent.parent.parent.parent / "scripts" / "runtime")
if _RUNTIME not in sys.path:
    sys.path.insert(0, _RUNTIME)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WorkflowSubmitRequest(BaseModel):
    plan: dict
    mode: str = "local"
    dry_run: bool = False


class StepOut(BaseModel):
    step: int
    skill: str
    status: str
    duration_ms: int = 0
    hitl_required: bool = False
    output_preview: str | None = None
    error: str | None = None


class WorkflowRunOut(BaseModel):
    run_id: str
    plan_id: str
    objective: str
    mode: str
    status: str
    total_steps: int
    completed_steps: int
    started_at: str | None
    completed_at: str | None


# ---------------------------------------------------------------------------
# Background execution
# ---------------------------------------------------------------------------

async def _run_workflow_background(
    run_id: str,
    plan: dict,
    dry_run: bool,
    db_url: str,
) -> None:
    """Execute a workflow plan in the background and persist results."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from execute_workflow import execute_local

    eng = create_async_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})
    Session = async_sessionmaker(eng, expire_on_commit=False)

    async with Session() as db:
        repo = WorkflowRepository(db)
        await repo.update_run_status(run_id, "running")
        await db.commit()

    loop = asyncio.get_event_loop()
    try:
        log = await loop.run_in_executor(None, execute_local, plan, dry_run)
    except Exception as exc:
        async with Session() as db:
            repo = WorkflowRepository(db)
            await repo.update_run_status(run_id, "failed")
            await db.commit()
        return

    final_status = log.get("status", "failed")
    async with Session() as db:
        repo = WorkflowRepository(db)
        await repo.update_run_status(run_id, final_status)
        for step in log.get("steps", []):
            await repo.upsert_step(
                run_id=run_id,
                step_number=step["step"],
                skill_name=step["skill"],
                status=step["status"],
                output_preview=(step.get("output") or "")[:500],
                error=step.get("error"),
                duration_ms=step.get("duration_ms", 0),
                hitl_required=step.get("hitl_required", False),
                hitl_reason=step.get("hitl_reason"),
            )
        await db.commit()

    await eng.dispose()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_workflow(
    body: WorkflowSubmitRequest,
    background_tasks: BackgroundTasks,
    user: Annotated[CurrentUser, Depends(require_permission("workflow:submit"))],
    db: AsyncSession = Depends(get_db),
):
    """Submit a workflow plan for execution. Returns immediately with run_id."""
    from app.config import get_settings

    plan = body.plan
    if not plan.get("skill_chain"):
        raise HTTPException(status_code=400, detail="plan.skill_chain is required and must be non-empty")

    import time, uuid
    run_id = f"RUN-{int(time.time())}-{uuid.uuid4().hex[:8]}"

    repo = WorkflowRepository(db, org_id=user.org_id)
    await repo.create_run(run_id, plan, mode="dry_run" if body.dry_run else body.mode)

    audit = AuditRepository(db, org_id=user.org_id)
    await audit.append(
        actor=f"human:{user.user_id}",
        action="submitted",
        resource_type="workflow",
        resource_id=run_id,
        run_id=run_id,
    )

    settings = get_settings()
    background_tasks.add_task(
        _run_workflow_background, run_id, plan, body.dry_run, settings.database_url
    )

    return {"run_id": run_id, "status": "queued"}


@router.get("")
async def list_workflows(
    user: Annotated[CurrentUser, Depends(require_permission("workflow:read"))],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    repo = WorkflowRepository(db, org_id=user.org_id)
    runs = await repo.list_runs(limit=limit, offset=offset)
    return [
        {
            "run_id": r.id,
            "objective": r.objective,
            "status": r.status,
            "total_steps": r.total_steps,
            "mode": r.mode,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


@router.get("/{run_id}")
async def get_workflow(
    run_id: str,
    user: Annotated[CurrentUser, Depends(require_permission("workflow:read"))],
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db, org_id=user.org_id)
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")
    return {
        "run_id": run.id,
        "plan_id": run.plan_id,
        "objective": run.objective,
        "mode": run.mode,
        "status": run.status,
        "total_steps": run.total_steps,
        "paused_at_step": run.paused_at_step,
        "failed_at_step": run.failed_at_step,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "steps": [
            {
                "step": s.step_number,
                "skill": s.skill_name,
                "status": s.status,
                "duration_ms": s.duration_ms,
                "hitl_required": s.hitl_required,
                "output_preview": s.output_preview,
                "error": s.error,
            }
            for s in (run.steps or [])
        ],
    }


@router.post("/{run_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_workflow(
    run_id: str,
    user: Annotated[CurrentUser, Depends(require_permission("workflow:cancel"))],
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db, org_id=user.org_id)
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")
    if run.status not in ("queued", "running", "paused_for_hitl"):
        raise HTTPException(status_code=409, detail=f"Cannot cancel run with status {run.status!r}")
    await repo.update_run_status(run_id, "cancelled")
    return {"run_id": run_id, "status": "cancelled"}