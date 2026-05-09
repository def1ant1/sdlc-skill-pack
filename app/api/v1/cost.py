"""
app/api/v1/cost.py — Workflow cost estimation endpoint.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, require_permission
from app.billing.cost_estimator import estimate_workflow_cost

router = APIRouter(prefix="/v1/cost", tags=["cost"])


class CostEstimateRequest(BaseModel):
    plan: dict


@router.post("/estimate")
async def estimate_cost(
    body: CostEstimateRequest,
    user: Annotated[CurrentUser, Depends(require_permission("cost:estimate"))],
):
    """Estimate token cost for a workflow plan before execution."""
    plan = body.plan
    skill_chain = plan.get("skill_chain", [])
    if not skill_chain:
        raise HTTPException(status_code=400, detail="plan.skill_chain is required")

    skills = [step.get("skill", "") for step in skill_chain]
    result = estimate_workflow_cost(skills)
    return result


@router.get("/pricing")
async def get_pricing(
    user: Annotated[CurrentUser, Depends(require_permission("cost:estimate"))],
):
    """Return current model pricing table."""
    from app.billing.pricing import MODEL_PRICING
    return MODEL_PRICING