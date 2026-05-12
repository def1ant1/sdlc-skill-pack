# Runtime Governance Enforcement

This document describes runtime governance controls implemented for `MB-P0-012`.

## Enforcement Flow

1. Runtime submits a permission request conforming to `schemas/skill-permission.schema.json`.
2. `scripts/governance/enforce_runtime_policy.py` evaluates:
   - Autonomous-mode prohibited actions.
   - High-risk side-effect actions requiring approval.
3. Requests with violations are denied (`fail_closed`) and emit a policy decision payload.
4. Regulated workflows invoke `scripts/governance/generate_evidence_pack.py` to persist audit evidence.

## Regulated Domains

Evidence-pack generation is enforced for workflows tagged with:

- `financial`
- `legal`
- `tax`
- `hr`
- `trading`
- `security`
- `logistics`
- `materials`

## Dashboard and Audit Integration

Policy decisions include a `dashboard_event` envelope with decision status and violation count, suitable for operator-console ingestion and auditable log pipelines.

## Cost enforcement hooks

- Before dispatch, call `/v1/cost/estimate` and compute projected budget consumption.
- If policy action is `block`, scheduler rejects execution and records a governance event.
- If policy action is `warn`, scheduler proceeds with operator-visible warning.

## MB-P2-007 domain enforcement addendum (2026-05-11)

- **Economics:** reports must attach explicit `source_timestamps` and `scenario_ranges` (base/upside/downside) for all forecasts and impact estimates.
- **Logistics:** booking, payment, and shipping document issuance actions must pause pending human approval.
- **Security:** IAM/policy/secret/DLP mutations must require explicit approval and must preserve evidence artifacts (pre-state, post-state, actor, timestamp, audit-log references).
- **Materials:** outputs that can affect safety, compliance, or structural integrity must be marked `safety_critical=true` and routed to professional review before operational use.

## Approval routing parity addendum (2026-05-12)

To preserve deterministic governance behavior, direct/manual executions and scheduled executions must both:

1. Generate a dry-run preview with step gates, side-effect classes, and missing-input checks.
2. Route high-risk gates into the same Approval Center queueing pathway.
3. Emit the same pause/resume/cancel runtime audit events tied to the same run identifier.
4. Persist policy context and decision rationale as evidence artifacts regardless of trigger origin.

This parity requirement ensures approval outcomes and evidence packs remain comparable across all runtime entry modes.
