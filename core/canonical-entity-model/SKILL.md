---
name: canonical-entity-model
description: Master entity definitions and golden-record schema for customers, vendors, products, and employees shared across all business domain operations.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - master-data-management
    - data-contract-registry

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

# Canonical Entity Model Skill

## Purpose

Defines and maintains the authoritative entity schema (customers, vendors, products, employees) used as the single source of truth across all business domain operations and integrations.