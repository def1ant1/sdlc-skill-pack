---
name: roi-estimation
description: Estimates delivered value and ROI relative to runtime costs for workflows and business outcomes.
priority: P1
metadata:
  version: "1.0.0"
  category: economics
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [runtime-economics, telemetry, token-cost-analysis]
telemetry_contract:
  events: [business_roi_estimated, business_value_to_cost_ranked]
---

# ROI Estimation

Computes value-to-cost rankings and ROI signals for budgeting and prioritization decisions.
