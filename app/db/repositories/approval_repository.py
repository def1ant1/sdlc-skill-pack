"""
app/db/repositories/approval_repository.py — HITL Approval lifecycle.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Approval


class ApprovalRepository:
    def __init__(self, db: AsyncSession, org_id: Optional[str] = None):
        self.db = db
        self.org_id = org_id

    async def create(
        self,
        run_id: str,
        step_number: int,
        skill_name: str,
        hitl_reason: str,
        risk_level: str = "L3",
        risk_score: int = 80,
        sla_hours: int = 24,
    ) -> Approval:
        approval = Approval(
            run_id=run_id,
            step_number=step_number,
            skill_name=skill_name,
            hitl_reason=hitl_reason,
            risk_level=risk_level,
            risk_score=risk_score,
            status="pending",
            sla_deadline=datetime.now(timezone.utc) + timedelta(hours=sla_hours),
        )
        self.db.add(approval)
        await self.db.flush()
        return approval

    async def get_pending(self, run_id: str) -> Optional[Approval]:
        q = select(Approval).where(
            Approval.run_id == run_id,
            Approval.status == "pending",
        )
        result = await self.db.execute(q)
        return result.scalar_one_or_none()

    async def list_pending(self) -> list[Approval]:
        q = select(Approval).where(Approval.status == "pending").order_by(Approval.requested_at)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def decide(
        self,
        approval_id: str,
        decision: str,
        decided_by: str,
        reason: str = "",
    ) -> None:
        await self.db.execute(
            update(Approval)
            .where(Approval.id == approval_id)
            .values(
                status=decision,
                decided_by=decided_by,
                decision_reason=reason,
                decided_at=datetime.now(timezone.utc),
            )
        )