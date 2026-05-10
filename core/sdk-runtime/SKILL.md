---
name: sdk-runtime
description: Loads, validates, and sandboxes third-party SDK skills within the Enterprise OS runtime boundary.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['agent-kernel', 'governance', 'local-security']

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

## Role

Enterprise OS control-plane service managing the complete lifecycle of third-party SDK skills:
package loading, manifest validation, sandboxed execution, capability enforcement, and resource
accounting. Every external skill invoked on the platform passes through this runtime to ensure
isolation, auditability, and governance compliance.

## Activation Triggers

- A marketplace skill is invoked for the first time (cold load required)
- A skill package version upgrade is detected requiring re-validation
- `governance` requests a capability audit of a loaded skill
- A sandboxed skill exceeds its declared resource quota (triggers suspension)
- `developer-portal` registers a newly certified skill package

## Execution Protocol

1. **Load package**: Fetch the skill package from the registry by package ID and version hash.
   Verify SHA-256 checksum against the signed manifest. Reject on checksum mismatch.

2. **Validate manifest**: Parse `sdk-manifest.yaml`. Confirm required fields: `name`, `version`,
   `capability_declarations`, `resource_quotas`, `sandbox_policy`. Reject packages declaring
   capabilities not in the approved capability taxonomy or missing governance fields.

3. **Sandbox construction**: Create an isolated execution environment:
   - File system: read-only mount of skill assets; no access to platform internals
   - Network: blocked by default; allow-listed endpoints declared in manifest only
   - Memory: enforce `resource_quotas.max_memory_mb`
   - CPU: enforce `resource_quotas.max_cpu_ms` per invocation
   - Secrets: inject only secrets explicitly granted by governance policy

4. **Execute**: Invoke the skill entry point with the request payload. Capture stdout/stderr,
   execution time, and peak resource consumption.

5. **Enforce quotas**: If execution time exceeds `max_cpu_ms` or memory exceeds limit,
   terminate the sandbox immediately and return `status: quota_exceeded`.

6. **Return and account**: Return structured output to the caller. Log the invocation record
   (skill_id, version, duration_ms, resource_used, status) to the audit trail.

## Output Format

```yaml
sdk_invocation:
  skill_id: "marketplace/skill-name@1.2.3"
  status: success | quota_exceeded | validation_failed | sandbox_error
  result: {}
  execution:
    duration_ms: 0
    memory_peak_mb: 0
    cpu_ms_used: 0
  sandbox_violations: []
  audit_ref: "SDK-INV-2026-xxxxx"
```

## References

- `references/` — SDK manifest schema, sandbox policy definitions, quota enforcement rules
