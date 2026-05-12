# Ecommerce Arbitrage + Negotiation + Finance/Tax Integration Guidance

## Scope
This guide defines output and governance requirements for regional arbitrage analysis, negotiation-support workflows, and finance/tax integration workflows.

## Arbitrage Requirements
- Regional scoring workflows must incorporate logistics-impact-aware opportunity scoring.
- Required scoring factors: landed-cost delta, lead-time risk, fulfillment constraints, expected margin, sell-through velocity, and downside risk.
- Outputs must remain support-only (`decision_mode: draft`) pending explicit approval for external actions.

## Negotiation Requirements
- Negotiation skills are advisory only and must include explicit **no-autonomous-commitment** controls.
- Disallowed autonomous actions include sending offers, signing agreements, issuing POs, and placing deposits/payments.
- Every recommendation must include a fallback strategy ladder and escalation trigger.

## Finance/Tax Requirements
- Tax and jurisdiction analysis outputs are preliminary and must set `professional_review_required: true`.
- Tax-facing actions (filings, remittances, registrations, legal positions) require qualified human review and explicit approval.
- Reconciliation outputs must include links to accounting entities where available:
  - `account_id`
  - `invoice_id`
  - `payment_id`
  - `order_id`
  - `marketplace_payout_id`

## Minimum Output Contract
- `decision_mode: draft`
- `approval_status: pending`
- `confidence`
- `assumptions`
- `evidence`
- `opportunity_score`
- `logistics_impact`
- `professional_review_required` (mandatory for tax/jurisdiction/accounting-affecting outputs)
- `accounting_links`
- `next_actions`
