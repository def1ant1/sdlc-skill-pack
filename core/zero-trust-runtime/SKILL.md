---
name: zero-trust-runtime
description: Enforces mTLS/JWT identity verification, continuous authorization, least-privilege enforcement, and network policy for all agent-to-agent communication.
metadata:
  version: "0.1.0"
  category: security
  owner: platform
  maturity: draft
  dependencies: ['governance', 'local-security', 'agent-kernel']
---

## Role

Zero-trust security enforcement layer for all agent-to-agent and skill-to-skill communication
in the Enterprise OS. Authenticates every caller identity via mTLS/JWT, evaluates
authorization against OPA policies on every request (not just at session start), enforces
least-privilege access, and detects policy violations for escalation to the
`security-architect-agent`.

## Activation Triggers

- Any inter-agent or inter-skill API call within the Enterprise OS (inline enforcement)
- A new agent or skill is registered (policy generation required)
- `zero-trust-policy-authoring` publishes a policy update (live policy reload)
- `lateral-movement-detection` signals an anomalous access pattern (immediate re-evaluation)
- `security-architect-agent` requests temporary access revocation for a compromised identity

## Execution Protocol

1. **Identity verification**: On every incoming request, extract the caller identity from
   the mTLS client certificate or JWT bearer token:
   - mTLS: verify client certificate chain against the platform CA; extract `agent_id` from CN
   - JWT: verify signature against platform JWKS; extract `sub` (agent_id) and `scope` claims
   - Reject with `401 Unauthorized` if verification fails

2. **Authorization evaluation**: Submit the authorization request to OPA:
   ```
   input = {
     caller: agent_id,
     target: target_skill_or_agent,
     action: requested_action,
     resource: resource_identifier,
     context: {timestamp, ip, session_id}
   }
   ```
   Apply the policy bundle. Return `ALLOW` or `DENY` with the matched policy rule.

3. **Least-privilege enforcement**: Verify the requested action scope is within the caller's
   declared `capability_declarations`. Reject requests for undeclared capabilities with `403`.

4. **Policy violation handling**: On `DENY`:
   - Return `403 Forbidden` with policy violation code
   - Emit `security.policy_violation` event on `event-bus`
   - If violation pattern matches lateral movement (same caller denied at 3+ targets in 5 minutes),
     escalate to `security-architect-agent`

5. **Audit logging**: Log every authorization decision (ALLOW and DENY) with full context
   for compliance evidence and forensic investigation.

## Output Format

```yaml
zero_trust_decision:
  request_id: "ZT-REQ-2026-xxxxx"
  caller: "cfo-agent"
  target: "erp-integration"
  action: "read_financial_data"
  decision: allow | deny
  policy_rule: "erp-integration.read.finance-agents"
  latency_ms: 2
  audit_ref: "ZT-AUD-2026-xxxxx"
```

## References

- `references/` — OPA policy bundle structure, mTLS certificate spec, JWT claims schema, policy violation taxonomy
