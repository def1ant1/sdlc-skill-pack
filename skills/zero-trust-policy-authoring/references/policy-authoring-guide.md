# Zero-Trust Policy Authoring — Policy Authoring Guide

## Policy Authoring Principles

1. **Default deny**: Every access request is denied unless explicitly permitted.
2. **Least privilege**: Grant the minimum permissions required for the declared function.
3. **Explicit context binding**: Permissions are bound to identity + device + time + risk score — not just identity alone.
4. **Immutable audit trail**: Every policy evaluation is logged; logs are tamper-evident.
5. **Human review for broad grants**: Any policy granting access to > 3 resources or `*` wildcard requires human approval.

---

## Policy Schema (OPA Rego Structure)

```rego
# Policy file: policies/<domain>/<policy-name>.rego
package apotheon.<domain>

import future.keywords.if
import future.keywords.in

# ─── Default: deny all ───────────────────────────────────────────────────────

default allow := false

# ─── Allow rule ──────────────────────────────────────────────────────────────

allow if {
    # 1. Identity verified
    identity_verified

    # 2. Device posture acceptable
    device_posture_acceptable

    # 3. Permission explicitly granted
    permission_granted

    # 4. Risk score within threshold
    input.context.risk_score <= 50
}

# ─── Sub-rules ───────────────────────────────────────────────────────────────

identity_verified if {
    input.principal.identity_verified == true
    input.principal.mfa_verified == true
    not token_expired
}

token_expired if {
    now := time.now_ns() / 1_000_000_000   # seconds
    input.auth.token_expiry < now
}

device_posture_acceptable if {
    input.device.posture_score >= data.thresholds.min_device_posture_score
    input.device.os_patched == true
    not input.device.jailbroken
}

permission_granted if {
    # Look up role → permissions mapping
    perms := data.rbac.role_permissions[input.principal.role]
    required_permission := sprintf("%s:%s", [input.resource.type, input.action])
    required_permission in perms
}
```

---

## Policy YAML Manifest

Every Rego policy is accompanied by a manifest for metadata and review tracking:

```yaml
policy_manifest:
  policy_id: "POL-ZTRUST-2026-xxxxx"
  policy_file: "policies/inference/model-access.rego"
  version: "1.2.0"

  description: "Controls which agents and skills may invoke the inference engine fleet"
  scope:
    resources: [inference-engine-fleet]
    actions: [invoke, health_check, manage_replicas]
    principals: [agent, skill, human_operator]

  risk_level: high    # low | medium | high | critical
  # High risk = any grant affecting production inference

  review:
    required: true
    last_reviewed_at: "2026-04-01T00:00:00Z"
    reviewed_by: "security-architect-agent"
    next_review_due: "2026-07-01"
    review_cadence_days: 90

  approval:
    required: true    # Because scope includes production resources
    approved_by: "cto"
    approved_at: "2026-04-01T10:00:00Z"

  test_cases:
    - description: "Agent with correct role and verified identity: allow"
      input:
        principal: {role: ml-engineer, identity_verified: true, mfa_verified: true}
        device: {posture_score: 85, os_patched: true, jailbroken: false}
        resource: {type: inference-engine-fleet}
        action: invoke
        context: {risk_score: 20}
        auth: {token_expiry: 9999999999}
      expected: {allow: true}

    - description: "Unverified identity: deny"
      input:
        principal: {role: ml-engineer, identity_verified: false, mfa_verified: true}
      expected: {allow: false}
```

---

## RBAC Role → Permission Mapping

```yaml
rbac:
  role_permissions:
    ml-engineer:
      - "inference-engine-fleet:invoke"
      - "inference-engine-fleet:health_check"
      - "model-registry:read"
      - "benchmark-results:read"

    sre-operator:
      - "inference-engine-fleet:manage_replicas"
      - "inference-engine-fleet:health_check"
      - "deployment:execute"
      - "monitoring:read"

    security-architect:
      - "zero-trust-runtime:policy_read"
      - "zero-trust-runtime:policy_write"
      - "audit-log:read"

    compliance-auditor:
      - "audit-log:read"
      - "compliance-runtime:read"
      - "control-catalog:read"

    agent:
      # Agents get the union of permissions for their declared skill scope
      # Resolved at runtime from skill manifest
      dynamically_resolved: true
```

---

## Policy Test Suite Requirements

Every policy must have test coverage for:

| Test Case Category | Required Coverage |
|-------------------|-------------------|
| Happy path (allow) | ≥ 3 positive cases with varied principal roles |
| Default deny | 1 case with no matching allow rule |
| Token expiry | 1 case with expired token |
| Low device posture | 1 case with posture_score below threshold |
| MFA not verified | 1 case |
| Risk score exceeded | 1 case with risk_score > threshold |
| Privilege escalation attempt | 1 case requesting unauthorized action |

Tests are run via `opa test policies/` in CI. Zero test failures required before policy deployment.

---

## Policy Deployment Process

```
1. Author Rego policy + YAML manifest
        │
        ▼
2. Run test suite locally: `opa test policies/<domain>/`
        │
        ▼
3. Submit PR to `apotheon-policies` repository
        │
        ▼
4. CI: opa check (syntax) + opa test (unit tests) + bundle lint
        │
        ▼
5. Security architect review (required for risk_level: high or critical)
        │
        ▼
6. Approval by policy owner
        │
        ▼
7. Merge → OPA bundle built and signed
        │
        ▼
8. Bundle distributed to zero-trust-runtime (pull every 60 seconds)
        │
        ▼
9. New policy active in evaluation engine
```