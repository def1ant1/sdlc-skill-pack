---
name: data-contract-registry
description: Registry and enforcement layer for data contracts between producers and consumers, with schema versioning, SLA tracking, and breaking-change detection.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - data-fabric
    - audit-trail

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

# Data Contract Registry Skill

## Purpose

Stores, versions, and enforces data contracts between upstream producers and downstream consumers. Detects breaking schema changes and alerts owning teams before they reach production.