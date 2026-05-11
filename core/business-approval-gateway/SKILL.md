---
name: business-approval-gateway
description: Human-in-the-loop approval routing for high-risk business workflow steps, with role-based escalation, SLA tracking, and audit-trail integration.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - audit-trail
    - policy-engine

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

# Business Approval Gateway Skill

## Purpose

Routes workflow steps requiring human approval to the appropriate approver based on role, risk tier, and policy rules. Tracks SLA compliance and escalates overdue approvals.