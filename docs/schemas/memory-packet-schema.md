# Memory Packet Schema

Defines the canonical structure for all memory packets used to preserve state
across SDLC phase transitions.

Produced and maintained by `core/orchestration/SKILL.md` Step 5.
Compressed and retrieved by `core/memory-token-management/SKILL.md`.
Validated by `scripts/validation/validate_memory_packet.py` (P5-002).

---

## Purpose

A memory packet is the single structured record of workflow state for a
multi-phase SDLC task. It replaces raw conversation history as the context
carried between phases. Every phase transition must produce an updated packet.

The packet is:
- **Human-readable**: YAML format, no abbreviations in field names
- **Compact**: contains decisions and artifacts, not reasoning transcripts
- **Verifiable**: every gate status, decision, and artifact is named and traceable
- **Evolvable**: new fields may be added under existing sections; existing required fields must not be removed

---

## Required vs Optional Fields

Fields marked `[required]` must be present and non-empty for the packet to be
valid. Fields marked `[optional]` may be omitted when not applicable.

---

## Schema

```yaml
memory_packet:

  # ── Identity ────────────────────────────────────────────────────────────────

  packet_id: [required]
    # Format: MP-<YYYYMMDD>-<NNN>
    # Unique per workflow instance. Increment NNN if multiple packets exist
    # for the same date and project.

  version: [required]
    # Packet schema version. Current: "1.0"

  created_at: [required]
    # ISO 8601 datetime when the packet was first created.

  updated_at: [required]
    # ISO 8601 datetime of the most recent update.

  workflow_plan_id: [optional]
    # ID of the Workflow Plan this packet corresponds to (WP-<date>-<NNN>).

  # ── Project Context ──────────────────────────────────────────────────────────

  project:
    name: [required]
      # Short human-readable name for the project or initiative.
    domain: [optional]
      # Business or technical domain (e.g., "AI-native API", "e-commerce platform").
    objective: [required]
      # The user's original goal in one sentence. Do not paraphrase or interpret.
    complexity: [required]
      # single-phase | multi-phase | full-sdlc

  # ── Phase Status ─────────────────────────────────────────────────────────────

  phase_status: [required]
    # Map of every SDLC phase in the workflow to its current status.
    # Only include phases that are part of the active skill chain.
    #
    # Status values: pending | in_progress | complete | blocked | skipped
    #
    # Example:
    #   requirements: complete
    #   architecture: complete
    #   ai-engineering: in_progress
    #   backend: pending
    #   security: pending

  current_phase: [required]
    # The phase currently executing. Must match one of the phase_status keys.

  # ── Decisions ─────────────────────────────────────────────────────────────────

  decisions:

    accepted: [required, may be empty list]
      # Decisions that have been made and are binding on downstream phases.
      # Each entry:
      - id: [required]           # DEC-NNN
        phase: [required]        # which phase made this decision
        decision: [required]     # one-sentence statement of what was decided
        rationale: [required]    # one-sentence reason
        adr_ref: [optional]      # path to ADR document if one was produced

    rejected: [optional]
      # Alternatives that were explicitly ruled out.
      # Each entry:
      - id: [required]
        phase: [required]
        option: [required]       # what was rejected
        reason: [required]       # one-sentence reason for rejection

    pending: [optional]
      # Decisions that must be made before a blocked phase can proceed.
      # Each entry:
      - id: [required]
        phase: [required]
        question: [required]     # what must be decided
        unblocks: [required]     # which phase or gate this decision unblocks
        owner: [optional]        # who must make this decision (user | team | stakeholder)

  # ── Constraints ───────────────────────────────────────────────────────────────

  constraints: [required, may have empty sub-lists]
    business:
      - [constraint statement]   # e.g., "Must launch before Q3 fiscal deadline"
    technical:
      - [constraint statement]   # e.g., "Must run on AWS; no GCP"
    security:
      - [constraint statement]   # e.g., "No PII may leave the EU data boundary"
    compliance:
      - [constraint statement]   # e.g., "Must meet SOC 2 Type II controls"
    ai_specific:
      - [constraint statement]   # e.g., "Model outputs must be explainable"

  # ── Artifacts ─────────────────────────────────────────────────────────────────

  artifacts: [required, may be empty list]
    # All artifacts produced or required across the workflow.
    # Each entry:
    - name: [required]           # artifact name (human-readable)
      type: [required]           # document | schema | spec | code | config | test | report
      phase: [required]          # which phase produced this artifact
      location: [required]       # file path, URL, or "inline" if embedded in packet
      status: [required]         # draft | complete | superseded
      consumed_by: [optional]    # list of phases or skills that need this artifact

  # ── Quality Gate Status ────────────────────────────────────────────────────────

  quality_gate_status: [required, may be empty list]
    # Record of every gate evaluation in the workflow.
    # Each entry:
    - gate_name: [required]
      transition: [required]     # "Phase A → Phase B"
      status: [required]         # PASS | PASS_WITH_WARNINGS | FAIL | NOT_EVALUATED | SKIPPED
      evaluated_at: [optional]   # ISO 8601 datetime
      criteria: [optional]
        - text: [required]
          result: [required]     # PASS | FAIL | WARN | SKIPPED
          note: [optional]       # explanation if result is not PASS
      remediation_tasks: [optional]
        - [task description]
      waiver_rationale: [optional]   # populated only when status is SKIPPED

  # ── Open Questions ────────────────────────────────────────────────────────────

  open_questions: [optional]
    # Unresolved questions that must be answered before a blocked phase proceeds.
    # Each entry:
    - id: [required]             # OQ-NNN
      question: [required]
      blocks: [required]         # which phase or gate this question blocks
      owner: [optional]

  # ── Risks ─────────────────────────────────────────────────────────────────────

  risks: [optional]
    # Active risks tracked across the workflow (from the workflow plan).
    # Each entry:
    - id: [required]             # RISK-NNN
      description: [required]
      severity: [required]       # high | medium | low
      phase: [required]
      status: [required]         # open | mitigated | accepted
      mitigation: [optional]

  # ── Token Stats ───────────────────────────────────────────────────────────────

  token_stats: [optional]
    # Running token budget tracking.
    total_budget: [optional]
    consumed: [optional]
    remaining: [optional]
    compression_triggered: [optional]    # true | false
    last_compression_at: [optional]      # ISO 8601 datetime

  # ── Next Action ───────────────────────────────────────────────────────────────

  next_action: [required]
    description: [required]      # first concrete step to execute from current state
    skill: [required]            # which skill to load next
    gate_just_passed: [optional] # name of gate that just cleared, enabling this action
    input_needed: [optional]     # what the user must provide before the next action can proceed
```

---

## Validation Rules

The following rules are enforced by `scripts/validation/validate_memory_packet.py`:

| Rule | Description |
|---|---|
| R1 | `packet_id` must match format `MP-\d{8}-\d{3}` |
| R2 | `version` must be a string matching a known schema version |
| R3 | `created_at` and `updated_at` must be valid ISO 8601 datetimes |
| R4 | `project.objective` must be non-empty |
| R5 | `project.complexity` must be one of: `single-phase`, `multi-phase`, `full-sdlc` |
| R6 | `phase_status` must contain at least one entry |
| R7 | Every phase in `phase_status` must use a valid status value |
| R8 | `current_phase` must exist as a key in `phase_status` |
| R9 | Every `decisions.accepted` entry must have `id`, `phase`, `decision`, `rationale` |
| R10 | Every `artifacts` entry must have `name`, `type`, `phase`, `location`, `status` |
| R11 | Every `quality_gate_status` entry must have `gate_name`, `transition`, `status` |
| R12 | `quality_gate_status[*].status` must be one of the five valid values |
| R13 | `next_action.description` and `next_action.skill` must be non-empty |
| R14 | A packet with any gate status of `FAIL` must not have a `current_phase` of `complete` for the phase after the failing gate's transition target |

---

## Lifecycle

```
Created       When a multi-phase workflow begins (Step 5 of orchestration protocol)
Updated       After every phase completion and gate evaluation
Compressed    When token_stats.consumed reaches compression_trigger threshold
              (compression preserves required fields; removes raw reasoning and
               superseded drafts — see core/memory-token-management/references/compression-rules.md)
Archived      When the workflow completes (all phases complete or terminal decision reached)
```

---

## Handoff Protocol

When passing the memory packet to a downstream skill:

1. Retrieve the current packet from its `location`.
2. Load only the sections the downstream skill needs:
   - Always: `project`, `current_phase`, `constraints`, `decisions.accepted`, `next_action`
   - If gate was just evaluated: `quality_gate_status` for the most recent gate
   - If artifacts are needed: `artifacts` filtered to `consumed_by` the current skill
3. Do not load the full packet into context if only a subset is needed.
4. After the downstream skill completes: update `phase_status`, `artifacts`, `quality_gate_status`, `next_action`, and `updated_at`.

---

## Relationship to Other References

| Document | Relationship |
|---|---|
| `core/memory-token-management/references/memory-schema.md` | Phase 0 stub this schema supersedes for Phase 1+ workflows |
| `core/memory-token-management/references/compression-rules.md` | Defines what to compress and when |
| `core/memory-token-management/references/retrieval-priorities.md` | Defines what to load first when budget is constrained |
| `shared/frameworks/quality-gates/catalog.md` | Source of gate names referenced in `quality_gate_status` |
| `scripts/validation/validate_memory_packet.py` | Enforces validation rules R1–R14 |