---
name: evidence-pack-generation
description: Governance support skill scaffold.
use_when:
  - Request requires this skill's governance workflow capability.
do_not_use_when:
  - Request is unrelated to governance workflows.
metadata:
  version: "1.0.0"
  owner: Apotheon.ai
  maturity: alpha
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# evidence-pack-generation

## Purpose
Provide evidence pack generation capabilities for governance workflows.

## Inputs
- Policy outcomes
- Event lineage

## Outputs
- Structured artifacts
