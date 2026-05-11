"""Workflow cost estimation and budget policy endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, require_permission
from app.billing.cost_estimator import estimate_workflow_cost, summarize_cost_events
from app.billing.quota import evaluate_budget_policy

router = APIRouter(prefix="/v1/cost", tags=["cost"])


class CostEstimateRequest(BaseModel):
    plan: dict
    consumed_today_usd: float = Field(default=0.0, ge=0.0)
    plan_tier: str = "starter"


class CostSummaryRequest(BaseModel):
    events: list[dict]


@router.post("/estimate")
async def estimate_cost(body: CostEstimateRequest, user: Annotated[CurrentUser, Depends(require_permission("cost:estimate"))]):
    plan = body.plan
    skill_chain = plan.get("skill_chain", [])
    if not skill_chain:
        raise HTTPException(status_code=400, detail="plan.skill_chain is required")

    skills = [step.get("skill", "") for step in skill_chain if step.get("skill")]
    result = estimate_workflow_cost(skills)
    decision = evaluate_budget_policy(body.consumed_today_usd, result["total_cost_usd"], body.plan_tier)
    result["budget_policy"] = decision.__dict__
    return result


@router.post("/summary")
async def cost_summary(body: CostSummaryRequest, user: Annotated[CurrentUser, Depends(require_permission("cost:estimate"))]):
    return summarize_cost_events(body.events)


@router.get("/pricing")
async def get_pricing(user: Annotated[CurrentUser, Depends(require_permission("cost:estimate"))]):
    from app.billing.pricing import MODEL_PRICING
    return MODEL_PRICING
