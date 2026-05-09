---
name: observability-platform
description: Prometheus metrics, OpenTelemetry distributed tracing, rolling benchmark baselines, and regression detection for all Apotheon workflow executions.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - sdlc-orchestration
    - audit-trail
---

# Observability Platform Skill

## Purpose

Provides the full observability stack: metrics scraping, distributed tracing, and automated performance regression detection across all skill executions.

## Components

### Prometheus Metrics (`app/observability/metrics.py`)

All metrics use the `apotheon_` prefix. Gracefully no-ops when `prometheus_client` not installed.

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `apotheon_workflow_runs_total` | Counter | status, mode | Total workflow runs |
| `apotheon_workflow_duration_seconds` | Histogram | mode | End-to-end duration |
| `apotheon_skill_calls_total` | Counter | skill_name, status | Skill executions |
| `apotheon_skill_latency_seconds` | Histogram | skill_name | Per-skill latency |
| `apotheon_token_usage_total` | Counter | skill_name, model, token_type | Token consumption |
| `apotheon_llm_call_duration_seconds` | Histogram | model | Claude API latency |
| `apotheon_llm_retries_total` | Counter | model, http_status | API retry attempts |
| `apotheon_hitl_gates_total` | Counter | skill_name, outcome | HITL triggers |
| `apotheon_hitl_pending` | Gauge | — | Workflows awaiting approval |
| `apotheon_memory_operations_total` | Counter | operation, tier | Memory read/write ops |
| `apotheon_memory_latency_seconds` | Histogram | tier | Memory operation latency |

Scrape endpoint: `GET /metrics` (Prometheus format)

### OpenTelemetry Tracing (`app/observability/tracing.py`)

```python
from app.observability.tracing import get_tracer

tracer = get_tracer("execute_workflow")
with tracer.start_as_current_span("workflow.execute") as span:
    span.set_attribute("run_id", run_id)
    span.set_attribute("skill_name", skill)
```

Exporters:
- **OTLP** (gRPC): set `OTEL_EXPORTER_OTLP_ENDPOINT` — sends to Jaeger/Tempo/Honeycomb
- **Console**: enabled at DEBUG level when no OTLP endpoint configured
- **Noop**: automatic fallback when `opentelemetry-sdk` not installed

### Benchmark Regression Detection (`app/observability/benchmark.py`)

Rolling p50/p95/p99 baselines computed over the last 30 completed runs per skill.

```python
from app.observability.benchmark import compute_baselines, detect_regression

# Called after workflow completion:
baselines = await compute_baselines(db)

# Called before each step:
regression = await detect_regression(db, skill_name="backend", observed_latency_ms=4200)
if regression:
    # ratio > 1.20 (20% above p95 baseline)
    await audit_repo.append(action="BENCHMARK_REGRESSION", detail=regression)
```

Regression threshold: 20% above p95 baseline (`REGRESSION_THRESHOLD = 0.20`).

## Grafana Dashboard

Recommended panels:
1. **Workflow throughput** — `rate(apotheon_workflow_runs_total[5m])`
2. **P95 skill latency** — `histogram_quantile(0.95, apotheon_skill_latency_seconds_bucket)`
3. **HITL rate** — `rate(apotheon_hitl_gates_total{outcome="triggered"}[1h])`
4. **Token burn rate** — `rate(apotheon_token_usage_total[1h])`
5. **LLM error rate** — `rate(apotheon_llm_retries_total[5m])`

## Alerting Rules

```yaml
# prometheus/rules/apotheon.yml
groups:
  - name: apotheon
    rules:
      - alert: HighSkillLatency
        expr: histogram_quantile(0.95, apotheon_skill_latency_seconds_bucket) > 30
        for: 5m
        labels:
          severity: warning

      - alert: HITLQueueBacklog
        expr: apotheon_hitl_pending > 10
        for: 10m
        labels:
          severity: critical

      - alert: LLMHighRetryRate
        expr: rate(apotheon_llm_retries_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `OTEL_SERVICE_NAME` | `apotheon` | OTel service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | OTLP gRPC endpoint (e.g. `http://jaeger:4317`) |
| `BENCHMARK_WINDOW_RUNS` | `30` | Rolling window for baseline computation |
| `REGRESSION_THRESHOLD` | `0.20` | P95 regression trigger fraction |

## Integration Points

- **`execute_workflow.py`** calls `record_workflow_run()`, `record_skill_call()`, `record_token_usage()`
- **`skill_activity.py`** calls `record_hitl_event()`, `record_llm_call()`
- **`app/main.py`** exposes `/metrics` and calls `setup_tracing()` at startup
- **`app/observability/benchmark.py`** is called by `app/api/v1/telemetry.py` for on-demand recompute