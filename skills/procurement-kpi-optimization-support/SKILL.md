---
name: procurement-kpi-optimization-support
description: Support-only procurement KPI recommendations linked to measurable baselines
  and human approvals for policy-impacting changes.
metadata:
  version: 9.0.0
  category: sdlc
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
use_when:
- Request clearly matches this skill's domain capabilities.
do_not_use_when:
- Request is outside this skill's domain or lacks required context.
---

# Procurement Kpi Optimization Support

## Role
Support-only procurement KPI recommendations linked to measurable baselines and human approvals for policy-impacting changes.

## Compliance Posture
- This skill is **support-only**: it may generate analysis and drafts, never final legal/HR/tax/payroll decisions.
- High-impact outputs must include `mandatory_review: true` and `review_owner` before release.
- External mutations and final determinations require explicit human approval.

## Integration
- Primary dependency: `core/master-data-management` for canonical entities, matching lineage, and survivorship context.
- Secondary controls: `core/policy-engine`, `core/business-approval-gateway`, and `core/audit-trail`.

## Guardrails
- Enforce bias/human-sensitive review for HR and legal contexts.
- Require explanation traces for threshold-based approvals and obligation updates.
- If confidence is low or policy context is missing, stop and escalate.
