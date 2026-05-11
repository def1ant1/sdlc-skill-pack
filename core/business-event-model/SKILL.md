---
name: business-event-model
description: Canonical event schema and routing bus for all business domain events enabling async coordination between finance, HR, legal, inventory, and customer operations.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - event-bus
    - canonical-entity-model

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
---

# Business Event Model Skill

## Purpose

Defines and enforces the canonical event schema for all business domain events, providing a shared vocabulary and routing bus for cross-domain async coordination.