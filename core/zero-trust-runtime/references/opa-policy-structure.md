# OPA Policy Bundle Structure & mTLS/JWT Specification

## Policy Bundle Layout

```
policy-bundle/
├── main.rego                  # Entry point — imports all domain policies
├── authz/
│   ├── agents.rego            # Agent-to-agent authorization rules
│   ├── skills.rego            # Skill-to-skill and agent-to-skill rules
│   ├── external.rego          # Platform-to-external-system rules
│   └── exceptions.rego        # Time-limited exception policies
├── data/
│   ├── capability_taxonomy.json   # Approved capability declarations
│   ├── source_credibility.json    # Source trust weights
│   └── exception_registry.json   # Active time-limited exceptions
└── tests/
    ├── agents_test.rego
    └── skills_test.rego
```

---

## Rego Policy Example

```rego
package authz.agents

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Allow if: caller is in allowed_callers for the target + action
allow if {
    input.action in allowed_actions[input.target]
    input.caller in allowed_callers[input.target][input.action]
    not is_suspended(input.caller)
    within_rate_limit(input.caller, input.target)
}

# cfo-agent is allowed to read financial data from erp-integration
allowed_callers["erp-integration"]["read_financial_data"] := {"cfo-agent"}
allowed_callers["erp-integration"]["read_financial_data"] := {"compliance-agent"}

# erp-integration read actions
allowed_actions["erp-integration"] := {"read_financial_data", "read_vendor_list"}

# Suspended agents are never allowed
is_suspended(agent_id) if {
    data.suspended_agents[agent_id].suspended == true
}

# Rate limit: max 60 requests/minute per caller+target pair
within_rate_limit(caller, target) if {
    count(data.request_log[caller][target]) < 60
}
```

---

## mTLS Certificate Specification

```yaml
platform_ca:
  common_name: "Enterprise OS Platform CA"
  key_algorithm: ECDSA P-384
  validity_years: 5
  is_root: true

agent_certificate:
  subject:
    common_name: "{agent_id}"              # e.g., "cfo-agent"
    organization: "Enterprise OS"
    organizational_unit: "Persistent Agents"
  key_algorithm: ECDSA P-256
  validity_days: 90                         # Rotate every 90 days
  extensions:
    key_usage: [digital_signature, key_encipherment]
    extended_key_usage: [client_auth, server_auth]
    san:
      dns: ["{agent_id}.agents.enterprise-os.internal"]

skill_certificate:
  subject:
    common_name: "{skill_name}"            # e.g., "erp-integration"
  validity_days: 90
  extensions:
    extended_key_usage: [server_auth]
```

---

## JWT Claims Schema

```json
{
  "sub": "cfo-agent",                       // Agent/skill identity (matches mTLS CN)
  "iss": "https://auth.enterprise-os.internal",
  "aud": "enterprise-os-api",
  "iat": 1746604800,                        // Issued at (Unix timestamp)
  "exp": 1746608400,                        // Expires: max 1 hour
  "scope": [
    "erp-integration:read_financial_data",
    "erp-integration:read_vendor_list",
    "notification-orchestration:send"
  ],
  "agent_type": "persistent_agent",         // persistent_agent | domain_skill | operator
  "domain": "finance",
  "trust_level": "high"                     // high | standard | provisional
}
```

---

## Policy Violation Taxonomy

| Code | Name | Severity | Auto-Response |
|------|------|----------|--------------|
| `PV-001` | Undeclared capability request | HIGH | DENY + alert |
| `PV-002` | Suspended agent access attempt | CRITICAL | DENY + immediate escalation |
| `PV-003` | Rate limit exceeded | MEDIUM | DENY (rate-limited) |
| `PV-004` | Expired JWT | LOW | DENY + re-auth prompt |
| `PV-005` | Deny storm (3+ denies in 5m) | CRITICAL | DENY + lateral-movement-detection alert |
| `PV-006` | Cross-namespace data access | HIGH | DENY + alert |
| `PV-007` | Off-hours sensitive access | MEDIUM | DENY + log for review |

---

## Authorization Decision Latency Budget

```
Target: p99 < 5ms for all authorization decisions

Components:
  - JWT validation (in-process): ~0.2ms
  - OPA policy evaluation (in-process): ~1.5ms
  - Rate limit check (Redis): ~1.0ms
  - Audit log write (async, non-blocking): 0ms on hot path

Total hot path: ~2.7ms
p99 budget headroom: 2.3ms
```