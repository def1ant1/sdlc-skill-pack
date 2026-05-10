---
name: system-architecture
description: Produces system architecture designs, ADRs, API boundaries, data flow decisions, quality attributes, and architectural risk analysis. Use when the user asks to design a system, define architecture, create an ADR, choose components, define service boundaries, or evaluate architectural tradeoffs.
metadata:
  version: 0.1.0
  category: architecture
  owner: Apotheon.ai
  maturity: foundation
  dependencies: [sdlc-memory-token-management]

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
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# System Architecture

## Mission

Create rigorous, secure, evolvable architecture artifacts for SDLC workflows.

## Required References

Use as needed:

- `references/architecture-workflow.md`
- `references/adr-guidance.md`
- `references/quality-attributes.md`

## Workflow

1. Clarify objective and system boundary.
2. Identify users, external systems, data flows, and constraints.
3. Produce architecture options when tradeoffs exist.
4. Recommend a decision with rationale.
5. Record major decisions using the ADR template.
6. Identify risks and quality gates.
7. Produce a memory packet for the next SDLC phase.

## Quality Gates

- Security assumptions identified.
- Data flows described.
- APIs or service boundaries defined.
- Tradeoffs documented.
- Risks and mitigations included.
- Next implementation step identified.
