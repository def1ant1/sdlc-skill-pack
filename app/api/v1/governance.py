"""
app/api/v1/governance.py — Policy management and governance dashboard.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, require_permission
from app.db.session import get_db
from app.db.models import Approval, Policy, PolicyEvaluation, WorkflowStep

router = APIRouter(prefix="/v1/governance", tags=["governance"])


class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    rule_expression: str
    action: str                 # BLOCK | WARN | REQUIRE_APPROVAL
    scope_pattern: str = "*"


@router.get("/dashboard")
async def governance_dashboard(
    user: Annotated[CurrentUser, Depends(require_permission("governance:dashboard"))],
    db: AsyncSession = Depends(get_db),
):
    """Aggregate governance metrics: policy violations, HITL rates, risk distribution."""
    # Policy violations (last 30 days)
    violations_q = select(
        PolicyEvaluation.policy_id,
        func.count(PolicyEvaluation.id).label("count"),
    ).where(
        PolicyEvaluation.result.in_(("block", "warn"))
    ).group_by(PolicyEvaluation.policy_id)
    violations_result = await db.execute(violations_q)
    violations = [{"policy_id": r.policy_id, "count": r.count} for r in violations_result]

    # HITL rate by skill
    hitl_q = select(
        WorkflowStep.skill_name,
        func.count(WorkflowStep.id).label("total"),
        func.sum(WorkflowStep.hitl_required.cast(db.bind.dialect.type_descriptor(
            __import__("sqlalchemy").Integer
        ))).label("hitl_count"),
    ).group_by(WorkflowStep.skill_name)
    hitl_result = await db.execute(hitl_q)
    hitl_rates = [
        {
            "skill_name": r.skill_name,
            "total_executions": r.total,
            "hitl_count": r.hitl_count or 0,
            "hitl_rate": round((r.hitl_count or 0) / r.total, 3) if r.total else 0,
        }
        for r in hitl_result
    ]

    # Pending approvals count
    pending_q = select(func.count(Approval.id)).where(Approval.status == "pending")
    pending_count = (await db.execute(pending_q)).scalar_one() or 0

    return {
        "pending_approvals": pending_count,
        "policy_violations": violations,
        "hitl_rates_by_skill": hitl_rates,
    }


@router.get("/policies")
async def list_policies(
    user: Annotated[CurrentUser, Depends(require_permission("policy:read"))],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Policy).where(Policy.is_active == True))
    policies = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "action": p.action,
            "scope_pattern": p.scope_pattern,
            "is_immutable": p.is_immutable,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in policies
    ]


@router.post("/policies", status_code=201)
async def create_policy(
    body: PolicyCreate,
    user: Annotated[CurrentUser, Depends(require_permission("policy:write"))],
    db: AsyncSession = Depends(get_db),
):
    if body.action not in ("BLOCK", "WARN", "REQUIRE_APPROVAL"):
        raise HTTPException(status_code=400, detail="action must be BLOCK, WARN, or REQUIRE_APPROVAL")

    policy = Policy(
        org_id=user.org_id,
        name=body.name,
        description=body.description,
        rule_expression=body.rule_expression,
        action=body.action,
        scope_pattern=body.scope_pattern,
        created_by=user.user_id,
    )
    db.add(policy)
    await db.flush()
    return {"id": policy.id, "name": policy.name, "status": "created"}


@router.get("/audit")
async def audit_chain(
    user: Annotated[CurrentUser, Depends(require_permission("governance:dashboard"))],
    db: AsyncSession = Depends(get_db),
):
    """Verify audit log chain integrity."""
    from app.db.repositories.audit_repository import AuditRepository
    repo = AuditRepository(db, org_id=user.org_id)
    return await repo.verify_chain()