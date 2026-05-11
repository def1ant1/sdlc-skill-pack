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
