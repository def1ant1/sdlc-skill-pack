"""
app/governance/risk_scorer.py — Composite risk scoring for workflow steps.

Produces a 0-100 risk score from multiple signals:
  - Skill inherent risk level (static table)
  - HITL history rate for the skill (from DB)
  - Compliance flag presence
  - Token volume (proxy for complexity)
  - Mode (temporal runs get a small boost for auditability)
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("apotheon.risk_scorer")

# Inherent risk scores per skill (0-100). Skills not listed default to 20.
SKILL_RISK_TABLE: dict[str, int] = {
    # High risk
    "cloud-deployment": 85,
    "infrastructure-provisioning": 85,
    "secret-rotation": 90,
    "database-migration": 80,
    "devsecops": 75,
    "release-management": 70,
    "incident-response": 70,
    "compliance-automation": 65,
    "sre": 60,
    # Medium risk
    "architecture": 45,
    "ai-engineering": 45,
    "backend": 35,
    "frontend": 30,
    "code-review": 30,
    "qa": 30,
    # Low risk
    "requirements": 20,
    "observability": 20,
    "executive-reporting": 15,
    "sdlc-orchestration": 10,
    "sdlc-memory-token-management": 10,
    "audit-trail": 5,
}

# Weights (must sum to 1.0)
_W_INHERENT = 0.50
_W_HITL_RATE = 0.25
_W_TOKEN_VOL = 0.10
_W_COMPLIANCE = 0.15


def base_risk(skill_name: str) -> int:
    """Return the static inherent risk score (0-100) for a skill."""
    return SKILL_RISK_TABLE.get(skill_name, 20)


def compute_risk_score(
    skill_name: str,
    hitl_rate: float = 0.0,          # 0.0-1.0 historical HITL trigger rate
    total_tokens: int = 0,            # input + output tokens
    compliance_flagged: bool = False,
    mode: str = "local",
) -> float:
    """
    Return a composite risk score in [0, 100].

    Args:
        skill_name: skill being scored
        hitl_rate: fraction of past executions that triggered HITL (0-1)
        total_tokens: total token volume for this step
        compliance_flagged: True if a compliance policy matched
        mode: 'local' | 'temporal' | 'dry_run'
    """
    inherent = base_risk(skill_name)

    # HITL history signal: scale 0-100
    hitl_signal = min(hitl_rate * 100, 100)

    # Token volume signal: log-scale, capped at 100k tokens → 100
    if total_tokens > 0:
        import math
        token_signal = min(math.log10(total_tokens + 1) / math.log10(100_001) * 100, 100)
    else:
        token_signal = 0.0

    # Compliance flag: binary bump
    compliance_signal = 100.0 if compliance_flagged else 0.0

    score = (
        _W_INHERENT * inherent
        + _W_HITL_RATE * hitl_signal
        + _W_TOKEN_VOL * token_signal
        + _W_COMPLIANCE * compliance_signal
    )

    # Dry-run: reduce risk (no side-effects)
    if mode == "dry_run":
        score *= 0.5

    return round(min(score, 100.0), 2)


def risk_level(score: float) -> str:
    """Categorize a score into LOW / MEDIUM / HIGH / CRITICAL."""
    if score < 25:
        return "LOW"
    if score < 50:
        return "MEDIUM"
    if score < 75:
        return "HIGH"
    return "CRITICAL"


async def fetch_hitl_rate(db, skill_name: str) -> float:
    """
    Query DB for the historical HITL trigger rate for a skill.
    Returns 0.0 if no data or DB unavailable.
    """
    try:
        from sqlalchemy import func, select
        from app.db.models import WorkflowStep

        q = select(
            func.count(WorkflowStep.id).label("total"),
            func.sum(
                WorkflowStep.hitl_required.cast(__import__("sqlalchemy").Integer)
            ).label("hitl_count"),
        ).where(WorkflowStep.skill_name == skill_name)

        result = await db.execute(q)
        row = result.one_or_none()
        if not row or not row.total:
            return 0.0
        return (row.hitl_count or 0) / row.total
    except Exception as exc:
        logger.debug("fetch_hitl_rate failed for %s: %s", skill_name, exc)
        return 0.0