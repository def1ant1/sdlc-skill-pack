"""
app/observability/metrics.py — Prometheus metrics for Apotheon runtime.

Import and call record_* functions from execute_workflow and skill_activity.
Expose via GET /metrics on the FastAPI app.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )
    _HAS_PROMETHEUS = True
except ImportError:
    _HAS_PROMETHEUS = False

if _HAS_PROMETHEUS:
    # Workflow-level metrics
    workflow_runs_total = Counter(
        "apotheon_workflow_runs_total",
        "Total workflow runs by status and mode",
        ["status", "mode"],
    )
    workflow_duration_seconds = Histogram(
        "apotheon_workflow_duration_seconds",
        "Workflow execution duration in seconds",
        ["mode"],
        buckets=[1, 5, 15, 30, 60, 120, 300, 600, 1800],
    )

    # Skill-level metrics
    skill_calls_total = Counter(
        "apotheon_skill_calls_total",
        "Total skill activity calls by skill name and status",
        ["skill_name", "status"],
    )
    skill_latency_seconds = Histogram(
        "apotheon_skill_latency_seconds",
        "Skill execution latency in seconds",
        ["skill_name"],
        buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120],
    )

    # LLM / token metrics
    token_usage_total = Counter(
        "apotheon_token_usage_total",
        "Total tokens used by skill and model",
        ["skill_name", "model", "token_type"],  # token_type: input | output
    )
    llm_call_duration_seconds = Histogram(
        "apotheon_llm_call_duration_seconds",
        "Claude API call latency in seconds",
        ["model"],
        buckets=[0.5, 1, 2, 5, 10, 20, 30, 60, 120],
    )
    llm_retries_total = Counter(
        "apotheon_llm_retries_total",
        "Total Claude API retry attempts",
        ["model", "http_status"],
    )

    # HITL metrics
    hitl_gates_total = Counter(
        "apotheon_hitl_gates_total",
        "Total HITL gate triggers by skill and outcome",
        ["skill_name", "outcome"],  # outcome: triggered | approved | rejected
    )
    hitl_pending_gauge = Gauge(
        "apotheon_hitl_pending",
        "Number of workflows currently paused for HITL",
    )

    # Memory metrics
    memory_operations_total = Counter(
        "apotheon_memory_operations_total",
        "Total memory operations by type and tier",
        ["operation", "tier"],  # operation: read|write, tier: qdrant|redis|postgres
    )
    memory_latency_seconds = Histogram(
        "apotheon_memory_latency_seconds",
        "Memory operation latency",
        ["tier"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2],
    )


# ---------------------------------------------------------------------------
# Recording helpers (no-ops when prometheus_client not installed)
# ---------------------------------------------------------------------------

def record_workflow_run(status: str, mode: str, duration_s: float) -> None:
    if not _HAS_PROMETHEUS:
        return
    workflow_runs_total.labels(status=status, mode=mode).inc()
    workflow_duration_seconds.labels(mode=mode).observe(duration_s)


def record_skill_call(skill_name: str, status: str, duration_s: float) -> None:
    if not _HAS_PROMETHEUS:
        return
    skill_calls_total.labels(skill_name=skill_name, status=status).inc()
    skill_latency_seconds.labels(skill_name=skill_name).observe(duration_s)


def record_token_usage(
    skill_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    if not _HAS_PROMETHEUS:
        return
    token_usage_total.labels(skill_name=skill_name, model=model, token_type="input").inc(input_tokens)
    token_usage_total.labels(skill_name=skill_name, model=model, token_type="output").inc(output_tokens)


def record_llm_call(model: str, duration_s: float, retry_count: int = 0, http_status: int = 200) -> None:
    if not _HAS_PROMETHEUS:
        return
    llm_call_duration_seconds.labels(model=model).observe(duration_s)
    if retry_count > 0:
        llm_retries_total.labels(model=model, http_status=str(http_status)).inc(retry_count)


def record_hitl_event(skill_name: str, outcome: str) -> None:
    if not _HAS_PROMETHEUS:
        return
    hitl_gates_total.labels(skill_name=skill_name, outcome=outcome).inc()


def record_memory_op(operation: str, tier: str, duration_s: float) -> None:
    if not _HAS_PROMETHEUS:
        return
    memory_operations_total.labels(operation=operation, tier=tier).inc()
    memory_latency_seconds.labels(tier=tier).observe(duration_s)


def get_metrics_response():
    """Return (content, content_type) tuple for the /metrics endpoint."""
    if not _HAS_PROMETHEUS:
        return b"# prometheus_client not installed\n", "text/plain"
    return generate_latest(), CONTENT_TYPE_LATEST