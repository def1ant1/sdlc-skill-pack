---
name: billing-runtime
description: Token usage tracking, cost estimation, quota enforcement, and per-org billing metering for all workflow executions.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - sdlc-orchestration
    - audit-trail

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# Billing Runtime Skill

## Purpose

The billing runtime tracks every token consumed by every skill execution, enforces per-org plan quotas, provides pre-flight cost estimates, and persists metering data for invoice generation.

## Components

### Cost Estimator (`app/billing/cost_estimator.py`)

Pre-execution estimation using benchmark baselines or static averages:

```python
from app.billing.cost_estimator import estimate_workflow_cost

result = estimate_workflow_cost(
    skills=["requirements", "architecture", "backend"],
    model="claude-sonnet-4-6",
)
# -> {"total_cost_usd": 0.042, "per_skill": [...], "note": "..."}
```

### Pricing Table (`app/billing/pricing.py`)

| Model | Input $/1M | Output $/1M |
|-------|-----------|------------|
| claude-opus-4-6 | $15.00 | $75.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-haiku-4-5 | $0.80 | $4.00 |

Override via `APOTHEON_MODEL_PRICING` env var (JSON string).

### Quota Enforcer (`app/billing/quota.py`)

| Plan Tier | Max Concurrent | Daily Tokens |
|-----------|---------------|--------------|
| free | 1 | 10K |
| starter | 3 | 100K |
| pro | 10 | 1M |
| enterprise | unlimited | unlimited |

```python
enforcer = QuotaEnforcer(db, org_id=org.id, plan_tier=org.plan_tier)
status = await enforcer.check_concurrent()
if not status.allowed:
    raise HTTPException(429, status.reason)
```

## Token Metering

After each skill execution, `execute_workflow.py` persists a `TokenUsage` record:

```sql
INSERT INTO token_usage (org_id, run_id, skill_name, model, input_tokens, output_tokens, cost_usd)
VALUES (?, ?, ?, ?, ?, ?, ?)
```

Aggregation endpoint: `GET /v1/telemetry/token-usage?days=30`

## Cost Estimate API

```http
POST /v1/cost/estimate
Authorization: Bearer <token>

{
  "plan": {
    "skill_chain": [
      {"skill": "requirements"},
      {"skill": "architecture"},
      {"skill": "backend"}
    ]
  }
}
```

Response:
```json
{
  "model": "claude-sonnet-4-6",
  "total_cost_usd": 0.042,
  "total_input_tokens": 5700,
  "total_output_tokens": 9500,
  "skills": [...]
}
```

## Audit Trail Integration

Every quota violation and billing event is emitted to `audit-trail`:
```
QUOTA_EXCEEDED  — concurrent limit reached
COST_THRESHOLD  — daily spend exceeds configured alert threshold
TOKEN_METERED   — successful token recording
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `APOTHEON_DEFAULT_MODEL` | `claude-sonnet-4-6` | Default model for estimation |
| `APOTHEON_MODEL_PRICING` | — | JSON override for pricing table |
| `BILLING_ALERT_THRESHOLD_USD` | `100.0` | Daily spend alert threshold |