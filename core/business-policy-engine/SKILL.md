---
name: business-policy-engine
description: Policy-as-Code evaluation engine for business domain rules covering spend authorization, vendor governance, workforce policy, and regulatory compliance enforcement.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - policy-engine
    - business-audit-ledger

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

# Business Policy Engine Skill

## Purpose

Evaluates business domain policies (spend limits, vendor tiers, workforce rules, regulatory mandates) against workflow steps before execution, with BLOCK/WARN/REQUIRE_APPROVAL enforcement modes.