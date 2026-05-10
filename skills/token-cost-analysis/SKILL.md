---
name: token-cost-analysis
description: Analyzes token usage and unit economics by model, workflow, and tenant
  to identify optimization opportunities.
priority: P1
metadata:
  version: 1.0.0
  category: economics
  owner: Apotheon.ai
  maturity: alpha
  dependencies:
  - runtime-economics
  - telemetry
telemetry_contract:
  events:
  - runtime_token_cost_computed
  - runtime_token_cost_anomaly
use_when:
- Request clearly matches this skill's domain capabilities.
do_not_use_when:
- Request is outside this skill's domain or lacks required context.
---

# Token Cost Analysis

Produces token-level cost analysis with rollups by skill/workflow/tenant/domain and optimization recommendations.
