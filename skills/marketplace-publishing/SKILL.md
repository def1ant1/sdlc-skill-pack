---
name: marketplace-publishing
description: Manages skill certification, publishing, versioning, and lifecycle operations within the Enterprise OS marketplace ecosystem.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['developer-portal', 'sdk-runtime', 'governance']
---

## Role

Skill lifecycle manager for the Enterprise OS marketplace. Guides skill authors through
the certification process, enforces quality and security gates, manages semantic versioning
and breaking-change detection, and handles the publish, deprecation, and retirement workflow
for all marketplace skills.

## Activation Triggers

- A skill author submits a new skill package for marketplace certification
- An existing certified skill submits a version update (patch, minor, or major)
- A certified skill receives a security vulnerability report
- A skill's maintenance window has elapsed without a qualifying update (deprecation trigger)
- `governance` requests a marketplace-wide security or capability audit
- `developer-portal` requests certification pipeline execution for a queued submission

## Execution Protocol

1. **Submission intake**: Accept a skill submission package:
   - Skill package tarball + `sdk-manifest.yaml`
   - `CHANGELOG.md` (required for version updates)
   - Certification tier requested: `community` | `certified` | `enterprise-grade`

2. **Automated quality gates**:
   - Schema validation: valid `sdk-manifest.yaml` with all required fields
   - Naming: kebab-case, unique in marketplace namespace
   - Versioning: valid semver; version must be higher than current published version
   - Breaking change detection: if major version bump, require migration guide in CHANGELOG
   - Documentation: SKILL.md must have complete Role, Activation Triggers, Execution Protocol, Output Format
   - Security scan: `sdk-runtime` sandbox smoke test with policy violation check

3. **Human review gate** (for `enterprise-grade` tier):
   - Route to security-architect-agent for capability declaration review
   - Human marketplace curator reviews documentation quality and use-case alignment

4. **Certification decision**: On all gates passed → `certified`. On any gate failed → `rejected`
   with specific failure reasons returned to the author.

5. **Publishing**: On certification → publish to `developer-portal`. Broadcast
   `marketplace.skill.published` event on `event-bus`. Update the capability discovery graph.

6. **Deprecation**: If a certified skill has no version updates in 12 months:
   - Mark as `deprecated` with a sunset date (90 days)
   - Notify registered users
   - On sunset date: retire from active listings (keep in archive for historical reference)

## Output Format

```yaml
certification_result:
  submission_id: "CERT-2026-xxxxx"
  skill_id: "marketplace/my-skill"
  version: "1.0.0"
  certification_tier: certified
  status: certified | rejected | pending_human_review
  gate_results:
    schema_validation: passed
    naming: passed
    security_scan: passed
    documentation: passed
    human_review: pending
  rejection_reasons: []
  published_at: null
```

## Quality Gates

- Zero certifications without automated quality gate pass
- Rejection reasons must be specific and actionable (not generic "failed")

## References

- `references/` — Certification gate specifications, semantic versioning policy, deprecation lifecycle
