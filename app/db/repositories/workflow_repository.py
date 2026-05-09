"""
app/db/repositories/workflow_repository.py — WorkflowRun and WorkflowStep persistence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import WorkflowRun, WorkflowStep


class WorkflowRepository:
    def __init__(self, db: AsyncSession, org_id: Optional[str] = None):
        self.db = db
        self.org_id = org_id  # injected by tenant middleware

    def _scope(self, q):
        """Apply org_id filter for tenant isolation."""
        if self.org_id:
            q = q.where(WorkflowRun.org_id == self.org_id)
        return q

    # ------------------------------------------------------------------
    # WorkflowRun
    # ------------------------------------------------------------------

    async def create_run(self, run_id: str, plan: dict, mode: str = "local") -> WorkflowRun:
        run = WorkflowRun(
            id=run_id,
            org_id=self.org_id,
            plan_id=plan.get("plan_id", ""),
            objective=plan.get("objective", ""),
            mode=mode,
            status="queued",
            total_steps=len(plan.get("skill_chain", [])),
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        q = self._scope(select(WorkflowRun).where(WorkflowRun.id == run_id))
        result = await self.db.execute(q.options(selectinload(WorkflowRun.steps)))
        return result.scalar_one_or_none()

    async def list_runs(self, limit: int = 20, offset: int = 0) -> list[WorkflowRun]:
        q = self._scope(
            select(WorkflowRun)
            .order_by(WorkflowRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def update_run_status(self, run_id: str, status: str, **kwargs) -> None:
        values = {"status": status, **kwargs}
        if status in ("completed", "failed", "cancelled"):
            values["completed_at"] = datetime.now(timezone.utc)
        await self.db.execute(
            update(WorkflowRun).where(WorkflowRun.id == run_id).values(**values)
        )

    async def count_running(self) -> int:
        q = select(func.count()).where(WorkflowRun.status.in_(("queued", "running")))
        if self.org_id:
            q = q.where(WorkflowRun.org_id == self.org_id)
        result = await self.db.execute(q)
        return result.scalar_one() or 0

    # ------------------------------------------------------------------
    # WorkflowStep
    # ------------------------------------------------------------------

    async def upsert_step(
        self,
        run_id: str,
        step_number: int,
        skill_name: str,
        status: str,
        **kwargs,
    ) -> WorkflowStep:
        q = select(WorkflowStep).where(
            WorkflowStep.run_id == run_id,
            WorkflowStep.step_number == step_number,
        )
        result = await self.db.execute(q)
        step = result.scalar_one_or_none()

        if step is None:
            step = WorkflowStep(
                run_id=run_id,
                step_number=step_number,
                skill_name=skill_name,
                status=status,
                started_at=datetime.now(timezone.utc),
                **kwargs,
            )
            self.db.add(step)
        else:
            step.status = status
            for k, v in kwargs.items():
                setattr(step, k, v)
            if status in ("completed", "failed", "error"):
                step.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return step