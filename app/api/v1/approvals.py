"""
app/api/v1/approvals.py — HITL approval queue and decision endpoints.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, require_permission
from app.db.session import get_db
from app.db.repositories.approval_repository import ApprovalRepository
from app.db.repositories.audit_repository import AuditRepository
from app.db.repositories.workflow_repository import WorkflowRepository

router = APIRouter(prefix="/v1/approvals", tags=["approvals"])


class DecisionRequest(BaseModel):
    decision: str           # "approved" | "rejected"
    reason: str = ""


@router.get("")
async def list_pending_approvals(
    user: Annotated[CurrentUser, Depends(require_permission("approval:read"))],
    db: AsyncSession = Depends(get_db),
):
    repo = ApprovalRepository(db, org_id=user.org_id)
    approvals = await repo.list_pending()
    return [
        {
            "approval_id": a.id,
            "run_id": a.run_id,
            "step_number": a.step_number,
            "skill_name": a.skill_name,
            "risk_level": a.risk_level,
            "risk_score": a.risk_score,
            "hitl_reason": a.hitl_reason,
            "status": a.status,
            "requested_at": a.requested_at.isoformat() if a.requested_at else None,
            "sla_deadline": a.sla_deadline.isoformat() if a.sla_deadline else None,
        }
        for a in approvals
    ]


@router.post("/{approval_id}/decide")
async def decide_approval(
    approval_id: str,
    body: DecisionRequest,
    user: Annotated[CurrentUser, Depends(require_permission("approval:decide"))],
    db: AsyncSession = Depends(get_db),
):
    if body.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    repo = ApprovalRepository(db, org_id=user.org_id)
    # Find approval by ID (simple select)
    from sqlalchemy import select
    from app.db.models import Approval
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail=f"Approval {approval_id!r} not found")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail=f"Approval already in status {approval.status!r}")

    await repo.decide(
        approval_id=approval_id,
        decision=body.decision,
        decided_by=user.user_id,
        reason=body.reason,
    )

    # Update workflow run status if approved
    wf_repo = WorkflowRepository(db, org_id=user.org_id)
    if body.decision == "approved":
        await wf_repo.update_run_status(approval.run_id, "running")
    else:
        await wf_repo.update_run_status(approval.run_id, "cancelled")

    # Audit the decision
    audit = AuditRepository(db, org_id=user.org_id)
    await audit.append(
        actor=f"human:{user.user_id}",
        action=body.decision,
        resource_type="approval",
        resource_id=approval_id,
        outcome="success",
        risk_level=approval.risk_level,
        run_id=approval.run_id,
    )

    return {
        "approval_id": approval_id,
        "run_id": approval.run_id,
        "decision": body.decision,
        "decided_by": user.user_id,
    }


@router.post("/runs/{run_id}/approve")
async def approve_run(
    run_id: str,
    body: DecisionRequest = DecisionRequest(decision="approved"),
    user: Annotated[CurrentUser, Depends(require_permission("approval:decide"))] = None,
    db: AsyncSession = Depends(get_db),
):
    """Shortcut: approve the pending approval for a run."""
    repo = ApprovalRepository(db, org_id=user.org_id if user else None)
    approval = await repo.get_pending(run_id)
    if not approval:
        raise HTTPException(status_code=404, detail=f"No pending approval for run {run_id!r}")

    await repo.decide(approval.id, "approved", user.user_id if user else "system", body.reason)
    wf_repo = WorkflowRepository(db)
    await wf_repo.update_run_status(run_id, "running")
    return {"run_id": run_id, "status": "approved"}


@router.post("/runs/{run_id}/reject")
async def reject_run(
    run_id: str,
    body: DecisionRequest = DecisionRequest(decision="rejected"),
    user: Annotated[CurrentUser, Depends(require_permission("approval:decide"))] = None,
    db: AsyncSession = Depends(get_db),
):
    """Shortcut: reject the pending approval for a run."""
    repo = ApprovalRepository(db, org_id=user.org_id if user else None)
    approval = await repo.get_pending(run_id)
    if not approval:
        raise HTTPException(status_code=404, detail=f"No pending approval for run {run_id!r}")

    await repo.decide(approval.id, "rejected", user.user_id if user else "system", body.reason)
    wf_repo = WorkflowRepository(db)
    await wf_repo.update_run_status(run_id, "cancelled")
    return {"run_id": run_id, "status": "rejected"}