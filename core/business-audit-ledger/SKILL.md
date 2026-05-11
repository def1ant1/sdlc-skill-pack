---
name: business-audit-ledger
description: Immutable append-only audit ledger for all business workflow events, decisions, and approvals with cryptographic chain integrity verification.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
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

# Business Audit Ledger Skill

## Purpose

Maintains an immutable, append-only audit trail for all business operations with hash-chained integrity so every decision and approval can be independently verified.