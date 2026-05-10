---
name: sdlc-skill-router
description: Deterministic routing control plane for resolving skill selection and dependency execution order.
use_when:
  - Deterministic routing or context reuse controls are requested.
do_not_use_when:
  - Task is a trivial single-skill request with no routing or cache concerns.
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

# sdlc-skill-router

## Role
Scaffold placeholder for backlog phase implementation.
