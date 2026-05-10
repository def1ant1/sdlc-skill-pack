---
name: developer-portal
description: Provides the registry API, marketplace, versioning, and discovery layer for the Enterprise OS SDK ecosystem.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['sdk-runtime', 'telemetry']

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

Registry and marketplace layer for the Enterprise OS SDK ecosystem. Manages skill package
publication, certification, versioning, semantic versioning enforcement, breaking-change
detection, and discovery APIs consumed by orchestration, sdk-runtime, and developers building
on the platform.

## Activation Triggers

- Developer submits a new skill package for certification
- A published skill package receives a version update
- `sdlc-orchestration` queries the marketplace for a skill matching a capability requirement
- Operator requests a skill catalog report (installed skills, versions, update availability)
- `governance` initiates a marketplace-wide capability audit

## Execution Protocol

1. **Receive submission**: Accept a skill package tarball and `sdk-manifest.yaml`. Assign
   a submission ID and begin certification pipeline.

2. **Static validation**: Verify manifest schema, kebab-case naming, semantic version format,
   required documentation fields, and declared dependency graph is acyclic.

3. **Sandbox smoke test**: Invoke `sdk-runtime` with a synthetic health-check request.
   Confirm the skill returns a valid response without sandbox violations.

4. **Governance review gate**: Submit capability declarations to `governance` for approval.
   Block certification if any declared capability requires elevated trust level not yet granted.

5. **Publish**: On approval, write the versioned package to the registry index. Update the
   discovery graph with new capability → skill mappings. Emit a `skill.published` event
   on the `event-bus`.

6. **Discovery API**: Answer capability-based queries (`find_skill(capability, min_version)`)
   by querying the registry index and returning ranked matches with compatibility metadata.

## Output Format

```yaml
portal_operation:
  operation: publish | certify | query | audit
  status: success | pending_review | rejected | not_found
  skill_id: "marketplace/skill-name"
  version: "1.2.3"
  certification_status: certified | provisional | rejected
  discovery_results: []  # For query operations
  audit_ref: "PORTAL-OPS-2026-xxxxx"
```

## References

- `references/` — Registry index schema, certification pipeline spec, discovery API contract
