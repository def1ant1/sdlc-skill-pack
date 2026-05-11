---
name: product-condition-estimation
description: Ecommerce sourcing and acquisition decision-support skill with scored opportunities, explicit assumptions, and approval-gated purchase pathways.
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

# Product Condition Estimation

## Role
Execute product condition estimation workflows while producing canonical, policy-aware decision-support artifacts.

## Scoring Model Requirements
All recommendations must include explicit component scores with a normalized 0-100 total:
- **margin_score**: expected net margin after fees, shipping, taxes, refurbishment, and holding costs.
- **velocity_score**: estimated sell-through speed based on demand, seasonality, and channel fit.
- **fraud_counterfeit_risk_score**: risk-adjusted penalty for title risk, authenticity concerns, and seller reliability.
- **confidence_score**: evidence quality score based on source freshness, comparables depth, and data completeness.

Default weighted model:
- acquisition_priority_score =
  - 0.40 * margin_score
  - 0.25 * velocity_score
  - 0.20 * (100 - fraud_counterfeit_risk_score)
  - 0.15 * confidence_score

## Recommendation Contract
Each recommendation must explicitly provide:
- rationale (why this opportunity or supplier is prioritized)
- assumptions (pricing, repair scope, resale channel, timeline)
- risk_profile (fraud/counterfeit, condition uncertainty, legal/logistics, liquidity)
- confidence and missing-evidence notes

## Approval Gates (Mandatory)
- Any purchase action pathway is **HITL-gated** and blocked by default.
- The skill may propose `request_approval` artifacts but must not execute commits, bids, deposits, POs, or payments.
- If approval context is missing or denied, fail closed and return decision-support only.

## Governance
- Always validate outputs against canonical entity/event schemas before emit.
- Require human approval before any external-system mutation or funds commitment.

## Workflow Artifact
See `examples/workflow.yaml`.
