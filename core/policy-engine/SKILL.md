---
name: policy-engine
description: Policy-as-Code evaluation engine with BLOCK/WARN/REQUIRE_APPROVAL actions, composite risk scoring, and pre-step governance enforcement for all workflow executions.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - audit-trail
    - sdlc-orchestration

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

# Policy Engine Skill

## Purpose

Evaluates Policy-as-Code rules against every workflow step before execution. Supports three enforcement modes: block execution, emit a warning, or escalate to HITL approval.

## Components

### Policy Engine (`app/governance/policy_engine.py`)

```python
from app.governance.policy_engine import PolicyEngine, EvalContext

engine = PolicyEngine(active_policies)
ctx = EvalContext(
    skill_name="cloud-deployment",
    risk_score=85.0,
    mode="local",
    user_role="developer",
)
results = engine.evaluate(ctx)

# Check outcomes
block = first_blocking_result(results)      # -> PolicyResult | None
needs_approval = requires_approval(results) # -> bool
warns = warnings(results)                   # -> list[PolicyResult]
```

### Rule DSL

Rules are restricted Python expressions evaluated in a sandboxed namespace. Available variables:

| Variable | Type | Description |
|----------|------|-------------|
| `skill_name` | str | Skill being executed |
| `risk_score` | float | Composite risk score 0-100 |
| `input_tokens` | int | Estimated input tokens |
| `output_tokens` | int | Estimated output tokens |
| `mode` | str | `local`, `temporal`, `dry_run` |
| `org_id` | str | Organization identifier |
| `user_role` | str | `viewer`, `developer`, `operator`, `admin` |
| `hitl_required` | bool | Whether HITL was triggered |
| `tags` | list[str] | Skill tags |

Example rules:
```python
# Block all deployments from viewer role
"skill_name == 'cloud-deployment' and user_role == 'viewer'"

# Require approval for high-risk steps
"risk_score > 70"

# Warn on excessive token usage
"input_tokens + output_tokens > 50000"

# Block temporal mode for free-tier (enforced via scope)
"mode == 'temporal' and org_id.startswith('free_')"
```

### Risk Scorer (`app/governance/risk_scorer.py`)

Composite 0-100 score from four signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Skill inherent risk | 50% | Static table (e.g. `cloud-deployment=85`) |
| Historical HITL rate | 25% | Fraction of past executions triggering HITL |
| Token volume | 10% | Log-scale, proxy for complexity |
| Compliance flag | 15% | Binary: compliance policy matched |

```python
from app.governance.risk_scorer import compute_risk_score, risk_level

score = compute_risk_score(
    skill_name="cloud-deployment",
    hitl_rate=0.4,
    total_tokens=8000,
    compliance_flagged=True,
    mode="local",
)
level = risk_level(score)  # -> "CRITICAL"
```

## Policy Enforcement Flow

```
execute_local() → before each step:
  1. Load active policies from DB (cached per request)
  2. Compute risk score (risk_scorer)
  3. Evaluate all policies (policy_engine.evaluate(ctx))
  4. If BLOCK: halt execution, emit POLICY_BLOCK audit event, raise error
  5. If REQUIRE_APPROVAL: pause run, create Approval record, emit HITL_GATE
  6. If WARN: log warning, emit POLICY_WARN audit event, continue
  7. Continue step execution
```

## Policy Management API

```http
GET  /v1/governance/policies          — list active policies
POST /v1/governance/policies          — create policy
GET  /v1/governance/dashboard         — violation metrics + HITL rates
GET  /v1/governance/audit             — verify audit chain integrity
```

Create policy example:
```json
{
  "name": "block-viewer-deployments",
  "description": "Viewers cannot trigger cloud deployments",
  "rule_expression": "skill_name == 'cloud-deployment' and user_role == 'viewer'",
  "action": "BLOCK",
  "scope_pattern": "cloud-deployment"
}
```

## Immutable System Policies

The following policies are seeded at startup and cannot be modified via API (`is_immutable=True`):

| Policy | Rule | Action |
|--------|------|--------|
| `block-unauthenticated` | `user_role == ''` | BLOCK |
| `require-approval-critical` | `risk_score >= 90` | REQUIRE_APPROVAL |
| `warn-high-risk` | `risk_score >= 70 and risk_score < 90` | WARN |

## Audit Integration

All policy enforcement actions are written to the `audit-trail`:

| Event | Trigger |
|-------|---------|
| `POLICY_BLOCK` | BLOCK action matched |
| `POLICY_WARN` | WARN action matched |
| `POLICY_APPROVAL_REQUIRED` | REQUIRE_APPROVAL matched |
| `POLICY_PASS` | No policies matched (logged at DEBUG) |

## Security Notes

- Rule DSL uses `eval()` with `{"__builtins__": {}}` — no built-in functions except the explicit allowlist
- Rule expressions are validated against a regex whitelist before evaluation
- Unsafe expressions are rejected with `(False, "unsafe expression rejected")` — fail-closed
- `is_immutable` policies cannot be deleted or modified via API; requires DB-level access