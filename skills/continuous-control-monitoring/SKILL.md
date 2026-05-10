---
name: continuous-control-monitoring
description: Evaluates SOC2/ISO 27001/HIPAA/GDPR/EU AI Act controls continuously and collects automated evidence via the compliance-runtime.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: draft
  dependencies: ['compliance-runtime', 'governance']

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

Control-level compliance evaluation engine. Implements the specific evaluation logic for
each control across the supported regulatory frameworks. Works as the execution layer
beneath `compliance-runtime`, which manages scheduling and posture scoring. Each control
evaluation produces a pass/fail result and collects the required evidence artifact.

## Activation Triggers

- `compliance-runtime` triggers a scheduled control evaluation
- A platform change event (new deployment, config change) may affect a specific control
- An on-demand audit requires immediate control re-evaluation
- Evidence for a control exceeds the freshness threshold

## Execution Protocol

1. **Control catalog lookup**: Retrieve the control definition for the requested control ID:
   - Evaluation method: automated query, telemetry check, configuration inspection, or manual
   - Evidence sources: which systems to query for evidence
   - Pass criterion: the specific condition that constitutes compliance
   - Evidence artifact type: log export, screenshot, configuration snapshot

2. **Automated evaluation examples**:

   **SOC2 CC6.1** (Logical access controls):
   - Query IdP: verify all admin accounts have MFA enabled
   - Check: `mfa_enabled_count / total_admin_count = 1.0`
   - Evidence: admin account roster with MFA status (timestamp, account list)

   **GDPR Article 32** (Security of processing):
   - Verify encryption at rest: check storage configuration for all data stores
   - Verify encryption in transit: inspect TLS certificate validity across all endpoints
   - Evidence: configuration snapshots with encryption settings

   **EU AI Act Article 9** (Risk management):
   - Check: AI system risk assessment document exists and was reviewed within 12 months
   - Check: high-risk AI systems have human oversight mechanisms configured
   - Evidence: risk assessment document reference + `hitl-dashboard` configuration export

3. **Evidence collection**: Retrieve and store the evidence artifact:
   - Compute SHA-256 hash of the evidence artifact
   - Store in the evidence vault with collection timestamp and evaluator identity
   - Return evidence vault reference to `compliance-runtime`

4. **Result reporting**: Return evaluation result to `compliance-runtime`:
   `{control_id, status: passing|failing, evidence_ref, evaluated_at, failure_reason}`

## Output Format

```yaml
control_evaluation:
  control_id: "SOC2-CC6.1"
  framework: soc2
  status: passing | failing | manual_review_required
  evidence_ref: "evidence-vault/SOC2-CC6.1-2026-05-07"
  evaluated_at: "2026-05-07T10:00:00Z"
  failure_reason: null
  next_evaluation_at: "2026-05-08T10:00:00Z"
```

## Quality Gates

- Evidence must be collected at evaluation time (no stale evidence for failing controls)
- Manual controls must create a task in `itsm-integration` for the human control owner

## References

- `references/` — Full control catalog (SOC2/ISO 27001/HIPAA/GDPR/EU AI Act), evaluation method library, evidence schema
