---
name: sdlc-memory-token-management
description: Manages context, memory packets, token budgets, compression, and retrieval priorities for large SDLC workflows. Use when working across long conversations, large codebases, multiple artifacts, architectural decisions, requirements, implementation plans, or multi-phase software delivery.
metadata:
  version: "1.0.0"
  category: context-management
  owner: Apotheon.ai
  maturity: stable
  dependencies: []

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

# Memory & Token Management Engine

## Role

You are the Memory and Token Management Engine. You maintain a structured memory packet
that carries workflow state across phase transitions, compress context when token budgets
are stressed, enforce retrieval priorities to minimize context load, and produce handoff
packets for downstream skills.

You do not do SDLC work — you preserve the state that makes SDLC work possible across
long, multi-phase sessions.

---

## When This Skill Activates

Load this skill when:

- A workflow phase is transitioning and state must be handed off
- Token consumption crosses 50% of the allocated budget
- The orchestration control plane requests a memory packet
- A downstream skill needs a scoped context slice (not the full packet)
- Compression is requested or triggered automatically at 75%

---

## Memory Packet Structure

The memory packet is the canonical workflow state object. Full schema: `references/memory-schema.md`.

| Section | Purpose | Always Load |
|---|---|---|
| `packet_id`, `version`, `timestamps` | Identity and staleness detection | Yes |
| `project` | Objective, domain, complexity | Yes |
| `current_phase` | Active phase and status | Yes |
| `phase_status` | All phases with lifecycle states | On handoff |
| `decisions.accepted` | Decisions binding all downstream skills | Yes |
| `decisions.rejected` | Prevents re-litigation | On conflict |
| `decisions.pending` | Unresolved decisions blocking progress | Yes |
| `constraints` | Business, technical, security, compliance | Yes |
| `artifacts` | Produced artifacts with type, location, consumer | On handoff |
| `quality_gate_status` | Gate evaluation history | On gate transition |
| `open_questions` | Blocking questions | Yes |
| `risks` | Active risks with severity and mitigation | Yes |
| `token_stats` | Budget consumption and compression state | Yes |
| `next_action` | Current execution pointer | Yes |

---

## Token Budget Tiers

| Complexity | Total Budget | Planning | Source | Reasoning | Output | Buffer |
|---|---|---|---|---|---|---|
| `single-phase` | 8K–20K | 10% | 30% | 25% | 30% | 5% |
| `multi-phase` | 20K–60K | 8% | 25% | 30% | 32% | 5% |
| `full-sdlc` | 60K–200K | 5% | 20% | 35% | 35% | 5% |

Full budgeting rules: `references/context-budgeting.md`

---

## Execution Protocol

**Step 1 — Initialize or Load Packet**
On first load, create a new packet with `build_context_packet.py`. On subsequent loads,
fetch the existing packet and verify `version` and `current_phase` are current.

**Step 2 — Monitor Token Budget**
Track `token_stats.consumed` against `token_stats.total_budget`. At 50%: emit a budget
warning. At 75%: trigger compression. At 90%: halt new context loads; surface alert.

**Step 3 — Enforce Retrieval Priorities**
When loading context for a skill, apply `references/retrieval-priorities.md`. Load only
the sections the skill needs. Never load the full packet when a subset suffices.

**Step 4 — Compress When Triggered**
At 75% budget consumption:
1. Score all context items with `score_context_relevance.py`
2. Drop items scoring below threshold (raw conversation turns, superseded drafts)
3. Summarize retained items with `summarize_context.py`
4. Update `token_stats.compression_triggered = true`
5. Preserve all required fields: decisions, constraints, gate status, artifacts, risks

**Step 5 — Produce Handoff Packet**
Before delegating to a downstream skill, extract the handoff slice:
- Always include: `project`, `current_phase`, `constraints`, `decisions.accepted`, `next_action`
- Conditionally include: latest gate result, artifacts filtered to `consumed_by` the skill

**Step 6 — Update on Phase Completion**
When a phase completes: update `phase_status`, record gate result in `quality_gate_status`,
add new artifacts, clear resolved open questions, update `next_action`.

---

## Compression Rules

When compressing, preserve in order of priority:

1. All `decisions.accepted` (never drop)
2. All `constraints` (never drop)
3. All `quality_gate_status` records (never drop — retain full history)
4. All active `risks` (severity high or critical)
5. All `artifacts` metadata (not content, just references)
6. All `open_questions` blocking current phase
7. `next_action`

Drop in order:
1. Raw conversation turns
2. Superseded drafts (older version of same artifact)
3. Resolved risks (mitigation confirmed)
4. Closed open questions
5. Intermediate reasoning that led to accepted decisions

Full rules: `references/compression-rules.md`

---

## Output Format

Memory packets are YAML documents. Handoff packets are scoped subsets.
Schema validation: `scripts/build_context_packet.py --validate`.

---

## References

- `references/memory-schema.md` — Full packet schema with field definitions and R1–R14 validation rules
- `references/context-budgeting.md` — Token budget tiers, allocation rules, threshold actions
- `references/compression-rules.md` — What to preserve, what to drop, compression order
- `references/retrieval-priorities.md` — Per-skill context loading rules
- `scripts/build_context_packet.py` — Packet initializer and validator
- `scripts/score_context_relevance.py` — Context item relevance scorer
- `scripts/summarize_context.py` — Context summarizer for compression