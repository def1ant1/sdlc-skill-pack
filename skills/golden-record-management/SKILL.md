---
name: golden-record-management
description: Assemble and steward golden records with survivorship and lineage controls
  integrated with master data management.
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

# Golden Record Management

## Role
Assemble and steward golden records with survivorship and lineage controls integrated with master data management.

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
