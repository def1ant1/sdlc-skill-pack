---
name: listing-seo-optimization
description: Listing Seo Optimization skill for ecommerce operations with draft mode and publish approval gates.
metadata:
  version: 0.1.0
  category: ecommerce
  owner: Marketplace Ops
  maturity: draft
  dependencies:
    - core/business-approval-gateway
---

# Listing Seo Optimization

## Mission
Support listing seo optimization decisions in **draft mode** by default; block publish actions pending explicit approval.

## Workflow
1. Ingest listing/catalog/SKU payload segmented by marketplace and sku.
2. Compute required ecommerce metrics where applicable: gross_margin, net_margin, sell_through, aging_days, return_rate, shipping_fee_ratio, conversion_rate, cac.
3. Generate recommendations and confidence with marketplace + SKU segmentation.
4. Emit `decision_mode: draft` output and `publish_ready: false` until approval gate passes.
5. Route publish request to business approval gateway with policy evidence.

## Approval Gates
- **Draft Gate (default pass):** Content generated and stored as non-published artifacts.
- **Publish Gate (required):** Requires approver, policy checks, and audit record before any marketplace mutation.

## Output Contract
- `decision_mode`: `draft | publish`
- `approval_status`: `pending | approved | denied`
- `segmentation`: `marketplace`, `sku`
- `metrics`: gross_margin, net_margin, sell_through, aging_days, return_rate, shipping_fee_ratio, conversion_rate, cac
