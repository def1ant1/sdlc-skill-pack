---
name: legal-operations-phase-pack
description: Cross-functional legal operations skill pack with support-only recommendations and mandatory human governance.
---

## Role
Provides orchestrated support workflows for legal/tax/entity/regulatory operations with KPI-linked recommendations and explicit evidence provenance.

## Governance
- Support-only output; no final legal, tax, payroll, or employment determinations.
- Mandatory review for recommendations at or above impact threshold.
- Human-sensitive bias checks required for HR/legal affected outputs.
- All findings must include structured decision-support metadata: jurisdiction, authority level, effective date, retrieved timestamp, verified timestamp, confidence, and professional-review requirement.
- Authoritative primary sources (statutes, regulations, agency bulletins, court/county/state/federal records) must be prioritized and cited.
- Filing/submission/mutation actions are approval-gated; emit approval request and hold until explicit decision.

## Integration
- Canonical entities from `core/master-data-management`.
- Policy, approvals, and audit lineage through core governance runtime.


## Governance References
- `docs/governance/professional-advice-boundaries.md`
- `docs/governance/legal-tax-decision-support-policy.md`
