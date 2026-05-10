---
name: vendor-obligation-tracking
description: Track supplier obligations, milestones, and SLA risks with approval thresholds for escalation.
metadata:
  version: "9.0.0"
  category: sdlc
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
---

# Vendor Obligation Tracking

## Role
Track supplier obligations, milestones, and SLA risks with approval thresholds for escalation.

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
