---
name: vendor-negotiation-support
description: Prepare vendor negotiation briefs with explicit no-autonomous-commitment controls.
metadata:
  version: 0.1.0
  category: ecommerce
  owner: Sourcing & Procurement
  maturity: draft
  dependencies:
    - core/business-approval-gateway
---

# Vendor Negotiation Support

## Mission
Provide decision support for vendor negotiation support in **draft mode** with explicit evidence, assumptions, and confidence scoring.

## Workflow
1. Ingest marketplace, product, region/jurisdiction, and counterpart data with timestamped source lineage.
2. Normalize economics across price, shipping, handling, taxes, fees, and return-risk assumptions.
3. Compute opportunity/risk outputs including logistics-impact-aware scoring where relevant.
4. Surface controls, confidence, unresolved data gaps, and required human decisions.
5. Emit support-only recommendations and approval-routing metadata before any external commitment.

## Control Boundaries
- **No autonomous commitment:** Must not place orders, send binding offers, sign contracts, file tax forms, or post accounting entries.
- **Human-in-the-loop required:** Any purchase, legal/tax filing, negotiation send, payout adjustment, or ledger mutation requires explicit approver authorization.
- **Professional review required:** Tax and jurisdiction conclusions are preliminary and must be reviewed by qualified finance/tax professionals before execution.

## Output Contract
- `decision_mode`: `draft`
- `approval_status`: `pending`
- `confidence`: `0..1`
- `assumptions`: explicit list of pricing/fee/tax/logistics assumptions
- `evidence`: source citations with retrieval timestamps
- `logistics_impact`: landed-cost delta, lead-time risk, and fulfillment constraints
- `opportunity_score`: weighted score with margin, velocity, risk, and complexity components
- `professional_review_required`: `true` for tax/jurisdiction/accounting-affecting outputs
- `accounting_links`: `account_id`, `invoice_id`, `payment_id`, `order_id`, `marketplace_payout_id` where applicable
- `next_actions`: recommended human approvals/escalations
