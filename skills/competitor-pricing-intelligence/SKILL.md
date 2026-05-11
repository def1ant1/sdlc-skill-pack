---
name: competitor-pricing-intelligence
description: Marketplace pricing intelligence skill for ecommerce extension.
metadata:
  version: 1.0.0
  category: ecommerce
  owner: Apotheon
  maturity: beta
use_when:
- Request requires competitor pricing intelligence workflows with channel and SKU-level outputs.
do_not_use_when:
- Task is unrelated to pricing intelligence or lacks marketplace context.
---

# competitor pricing intelligence

## Role
Provide structured analysis for competitor pricing intelligence in marketplace operations.

## Inputs
- SKU-level price and cost data.
- Marketplace profile with fee, shipping, and tax assumptions.

## Outputs
- Normalized economics by channel.
- Margin/profit diagnostics with confidence scoring where relevant.
