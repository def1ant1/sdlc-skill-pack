---
name: sdlc-memory-token-management
description: Manages context, memory packets, token budgets, summarization, and retrieval priorities for large SDLC workflows. Use when working across long conversations, large codebases, multiple artifacts, architectural decisions, requirements, implementation plans, or multi-phase software delivery.
metadata:
  version: 0.1.0
  category: context-management
  owner: Apotheon.ai
  maturity: foundation
  dependencies: []
---

# SDLC Memory and Token Management

## Mission

Keep SDLC workflows coherent across long sessions while minimizing context load.

## Always Preserve

- latest user instruction
- current objective
- accepted decisions
- hard constraints
- active artifacts
- unresolved risks
- next action

## Compression Rule

When context grows, preserve decisions and constraints before details.

## References

- `references/context-budgeting.md`
- `references/memory-schema.md`
- `references/compression-rules.md`
- `references/retrieval-priorities.md`

## Handoff Format

```yaml
memory_packet:
  project:
  phase:
  decisions:
  constraints:
  artifacts:
  risks:
  next_action:
```
