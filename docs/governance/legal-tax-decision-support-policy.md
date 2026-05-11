# Legal/Tax Decision-Support Policy

## Purpose
This policy defines enforceable boundaries for legal, tax, entity-management, and regulatory intelligence skills.

## Binding Boundaries
- Outputs are decision support only and must not be represented as final legal or tax advice.
- Final determinations and production filings require qualified professional review.
- Skills must include non-advisory disclaimers when producing recommendations.

## Required Finding Schema
Every legal/tax/regulatory finding must include:
- `jurisdiction`
- `authority_level`
- `effective_date`
- `retrieved_at` (ISO-8601 timestamp)
- `verified_at` (ISO-8601 timestamp)
- `confidence` (0.0-1.0)
- `professional_review_required` (boolean)

## Citation Requirements
- Prioritize authoritative primary sources: statutes/codes, regulations, agency guidance, and court records.
- Secondary commentary may be used only when primary sources are unavailable and this limitation is explicitly flagged.
- Citation lineage must be retained for audit.

## Approval Gates
The following actions require explicit human approval before execution:
- Filings and submissions to agencies/courts/tax authorities.
- Regulatory actions with external effect.
- Tax, legal-entity, or compliance-record mutations.

If approval is absent, workflow must emit `approval_requested` and remain in hold state.
