"""
app/observability/benchmark.py — Rolling benchmark baseline and regression detection.

After each workflow completion, computes p50/p95/p99 latency baselines
per skill over the last N runs and emits a BENCHMARK_REGRESSION audit event
if p95 latency exceeds the stored baseline by more than REGRESSION_THRESHOLD.
"""
from __future__ import annotations

import logging
import statistics
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BenchmarkBaseline, WorkflowStep

logger = logging.getLogger("apotheon.benchmark")

REGRESSION_THRESHOLD = 0.20   # 20% above baseline triggers a regression event
WINDOW_RUNS = 30               # rolling window size


async def compute_baselines(db: AsyncSession, skill_name: Optional[str] = None) -> list[dict]:
    """
    Compute and persist p50/p95/p99 baselines for all skills (or one skill).
    Returns list of baseline dicts.
    """
    q = (
        select(WorkflowStep.skill_name, WorkflowStep.duration_ms, WorkflowStep.status,
               WorkflowStep.input_tokens, WorkflowStep.output_tokens)
        .where(WorkflowStep.status == "completed")
    )
    if skill_name:
        q = q.where(WorkflowStep.skill_name == skill_name)
    result = await db.execute(q)
    rows = result.all()

    # Group by skill
    by_skill: dict[str, list] = {}
    for row in rows:
        by_skill.setdefault(row.skill_name, []).append(row)

    baselines = []
    for name, records in by_skill.items():
        if len(records) < 3:
            continue  # not enough data

        recent = sorted(records, key=lambda r: 0)[-WINDOW_RUNS:]
        latencies = [r.duration_ms for r in recent if r.duration_ms]
        input_toks = [r.input_tokens for r in recent if r.input_tokens]
        output_toks = [r.output_tokens for r in recent if r.output_tokens]

        if not latencies:
            continue

        latencies.sort()
        p50 = statistics.median(latencies)
        n = len(latencies)
        p95 = latencies[int(n * 0.95)]
        p99 = latencies[int(n * 0.99)]

        baseline = BenchmarkBaseline(
            skill_name=name,
            window_runs=len(recent),
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            avg_input_tokens=statistics.mean(input_toks) if input_toks else None,
            avg_output_tokens=statistics.mean(output_toks) if output_toks else None,
            success_rate=sum(1 for r in recent if r.status == "completed") / len(recent),
        )
        db.add(baseline)
        baselines.append({
            "skill_name": name,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
            "window_runs": len(recent),
        })

    await db.flush()
    return baselines


async def detect_regression(
    db: AsyncSession,
    skill_name: str,
    observed_latency_ms: float,
) -> Optional[dict]:
    """
    Compare observed latency against stored p95 baseline.
    Returns a regression dict if threshold exceeded, else None.
    """
    q = (
        select(BenchmarkBaseline)
        .where(BenchmarkBaseline.skill_name == skill_name)
        .order_by(BenchmarkBaseline.computed_at.desc())
        .limit(1)
    )
    result = await db.execute(q)
    baseline = result.scalar_one_or_none()
    if not baseline or not baseline.p95_latency_ms:
        return None

    ratio = observed_latency_ms / baseline.p95_latency_ms
    if ratio > (1 + REGRESSION_THRESHOLD):
        regression = {
            "skill_name": skill_name,
            "observed_ms": observed_latency_ms,
            "baseline_p95_ms": baseline.p95_latency_ms,
            "ratio": round(ratio, 3),
            "threshold": REGRESSION_THRESHOLD,
        }
        logger.warning(
            "BENCHMARK_REGRESSION %s: %.0fms observed vs p95=%.0fms (%.0f%% above threshold)",
            skill_name, observed_latency_ms, baseline.p95_latency_ms,
            (ratio - 1) * 100,
        )
        return regression
    return None