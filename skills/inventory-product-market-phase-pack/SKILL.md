---
name: inventory-product-market-phase-pack
description: Phase-pack skill for inventory, product, and market intelligence operations using canonical entity/event contracts.
metadata:
  version: 9.0.0
  category: business-operations
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
use_when:
- Request spans inventory/product/market phases and requires governed recommendations.
do_not_use_when:
- Request is outside supply, product, or market decision support scope.
---

# Inventory, Product & Market Phase Pack

## Role
Drive MB-P2-003 inventory/product/procurement/market workflows with schema-valid canonical outputs and approval-gated side effects.

Covered capabilities include demand planning, sku margin analysis, stockout detection, supplier/vendor risk intelligence, procurement routing, and scarcity/arbitrage analysis for acquisition and pricing support.

## Contracts & Context Loading
- Use canonical schemas for product/order/workflow/decision/task and approval/workflow events.
- Load context progressively: product and order entities, policy context, then market signals.
- Enforce token budgets to preserve room for rationale and fallback instructions.

## Governance
- Human approval is mandatory for any customer-facing update.
- Human approval is mandatory for external mutations (supplier portal updates, catalog repricing, PO changes, listing publication, and vendor outreach).
- Scraping tasks must validate robots directives, terms-of-use constraints, connector rate limits, and explicit operator approval before any non-public or high-frequency collection.
- If approval is absent, emit approval_requested and hold execution.

## Failure & Fallback
- Missing data contracts -> emit safe summary and request remediation.
- Schema non-compliance -> reject mutation and generate corrected artifact template.
- External system unavailable -> defer with retry ticket and operator handoff.

## Example workflow
See `examples/workflow.yaml`.
