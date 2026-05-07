---
name: sdk-authoring
description: Provides SDK scaffolding, authoring workflows, and testing utilities for building, testing, and packaging third-party Enterprise OS skills.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['sdk-runtime', 'developer-portal']
---

## Role

Developer experience layer for Enterprise OS skill authoring. Generates compliant skill
scaffolds, provides authoring guidance, validates skill packages against the SDK schema
before submission, and runs local sandbox tests so authors can iterate before entering
the formal certification pipeline.

## Activation Triggers

- A developer requests a new skill scaffold for a specific skill type
- A skill author requests pre-certification validation of a work-in-progress package
- A skill package fails certification and the author needs diagnostic guidance
- `developer-portal` provides an authoring tutorial invocation
- Operator onboards a new development team to the Enterprise OS SDK

## Execution Protocol

1. **Scaffold generation**: Generate a complete, compliant skill scaffold from a template:
   - `sdk-manifest.yaml` with all required fields pre-filled from author input
   - `SKILL.md` with section stubs matching the platform convention
   - `references/` directory with placeholder file
   - Example test request and expected response
   - GitHub Actions CI workflow for local validation

2. **Manifest guidance**: Interactively guide the author through required manifest fields:
   - `capability_declarations`: explain the capability taxonomy; warn about over-broad declarations
   - `resource_quotas`: provide sizing guidelines based on skill workload profile
   - `sandbox_policy`: explain allow-list network policy and when to request exemptions

3. **Pre-certification validation**: Run the full certification gate suite locally
   (without the human review gate). Return specific, actionable feedback for each gate:
   - "FAIL: description field exceeds 1024 characters (current: 1156)"
   - "WARN: network allow-list includes `*.external.com` — consider narrowing scope"

4. **Local sandbox test**: Run the skill in the `sdk-runtime` sandbox with a developer-provided
   test request. Return: response, execution time, memory peak, any sandbox violations.

5. **Submission preparation**: When the skill passes all pre-certification checks, generate
   the submission package (tarball + manifest + CHANGELOG) and submit to `developer-portal`.

## Output Format

```yaml
sdk_authoring:
  operation: scaffold | validate | sandbox_test | submit
  skill_id: "marketplace/my-new-skill"
  status: success | validation_failed | sandbox_error
  validation_results:
    gates_passed: 0
    gates_failed: 0
    warnings: []
    errors: []
  sandbox_result:
    status: success | quota_exceeded | sandbox_error
    execution_time_ms: 0
    memory_peak_mb: 0
    violations: []
  submission_ref: null
```

## Quality Gates

- Scaffold must produce a package that passes pre-certification validation out-of-the-box
- Local sandbox test must use the same sandbox configuration as `sdk-runtime` production

## References

- `references/` — SDK manifest field guide, capability taxonomy, scaffold template library
