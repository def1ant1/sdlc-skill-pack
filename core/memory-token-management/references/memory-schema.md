# Memory Packet Schema

Used by `core/memory-token-management/SKILL.md` and `core/orchestration/SKILL.md` to define
the canonical structure, field definitions, and validation rules for workflow memory packets.

---

## Full Schema

```yaml
memory_packet:

  # Identity
  packet_id: "MP-YYYYMMDD-NNN"           # Unique ID; regenerated on each compression
  version: "1.0.0"                         # Schema version (not workflow version)
  created_at: "2026-05-06T00:00:00Z"      # ISO 8601
  updated_at: "2026-05-06T00:00:00Z"      # Updated on every write
  compression_generation: 0               # Increments each time compression runs

  # Project identity
  project:
    name: ""                              # Project name
    objective: ""                         # User's goal, verbatim
    domain: ""                            # e.g. "ai-document-processing"
    complexity: "single-phase | multi-phase | full-sdlc"
    workflow_plan_id: "WP-YYYYMMDD-NNN"   # Reference to originating workflow plan

  # Current execution state
  current_phase: ""                       # Active phase name
  next_action: ""                         # Concrete next step

  # Per-phase lifecycle status
  phase_status:
    requirements: "not_started | in_progress | complete | skipped | blocked"
    architecture: "not_started | in_progress | complete | skipped | blocked"
    ai-engineering: "not_started | in_progress | complete | skipped | blocked"
    backend: "not_started | in_progress | complete | skipped | blocked"
    frontend: "not_started | in_progress | complete | skipped | blocked"
    security: "not_started | in_progress | complete | skipped | blocked"
    qa: "not_started | in_progress | complete | skipped | blocked"
    release: "not_started | in_progress | complete | skipped | blocked"
    observability: "not_started | in_progress | complete | skipped | blocked"
    operations: "not_started | in_progress | complete | skipped | blocked"
    compliance: "not_started | in_progress | complete | skipped | blocked"
    reporting: "not_started | in_progress | complete | skipped | blocked"

  # Decision log
  decisions:
    accepted:
      - id: "DEC-001"
        phase: ""
        decision: ""                      # What was decided
        rationale: ""                     # Why
        timestamp: ""
    rejected:
      - id: "DEC-002"
        phase: ""
        decision: ""
        reason: ""                        # Why rejected
        timestamp: ""
    pending:
      - id: "DEC-003"
        phase: ""
        question: ""                      # Decision to be made
        options: []
        blocking: true | false

  # Constraints (never drop during compression)
  constraints:
    business: []                          # Budget, timeline, team size, market
    technical: []                         # Language, framework, platform
    security: []                          # Auth requirements, data classification
    compliance: []                        # Regulatory requirements
    ai_specific: []                       # Model constraints, bias rules, explainability

  # Produced artifacts
  artifacts:
    - id: "ART-001"
      type: "document | code | schema | config | diagram"
      name: ""
      location: ""                        # File path or URL
      phase: ""                           # Phase that produced it
      status: "draft | final | superseded"
      consumed_by: []                     # Skills that need this artifact

  # Quality gate history (retain all records, never drop)
  quality_gate_status:
    - gate: "requirements-complete"
      status: "PASS | FAIL | PASS_WITH_WARNINGS | NOT_EVALUATED | SKIPPED"
      evaluated_at: ""
      evidence: []
      failures: []
      prior_fail_ref: null               # Reference to previous FAIL record if remediated

  # Blocking questions
  open_questions:
    - id: "OQ-001"
      phase: ""
      question: ""
      blocking_gate: ""                  # Which gate this blocks
      raised_at: ""
      resolved: false

  # Active risks
  risks:
    - id: "RISK-001"
      phase: ""
      description: ""
      severity: "low | medium | high | critical"
      mitigation: ""
      status: "open | mitigated | accepted | closed"

  # Token budget tracking
  token_stats:
    total_budget: 0
    consumed: 0
    remaining: 0
    compression_triggered: false
    compression_generation: 0
    last_compression_at: null
    budget_tier: "single-phase | multi-phase | full-sdlc"
```

---

## Validation Rules

| Rule | Field | Requirement |
|---|---|---|
| R1 | `packet_id` | Non-empty; matches `^MP-[0-9]{8}-[0-9]{3}$` |
| R2 | `project.objective` | Non-empty |
| R3 | `project.complexity` | One of: `single-phase`, `multi-phase`, `full-sdlc` |
| R4 | `current_phase` | Non-empty; matches a known phase name |
| R5 | `next_action` | Non-empty |
| R6 | `decisions.accepted` | Each entry has `id`, `decision`, `rationale` |
| R7 | `constraints` | At least one constraint category present |
| R8 | `phase_status` | All statuses are valid enum values |
| R9 | `quality_gate_status` | All FAIL records retained (not dropped by compression) |
| R10 | `open_questions` | Each entry has `id`, `question`, `blocking_gate` |
| R11 | `risks` | Each entry has `id`, `severity`, `status` |
| R12 | `token_stats.total_budget` | Integer > 0 |
| R13 | `token_stats.consumed` | Integer ≥ 0; ≤ `total_budget` |
| R14 | `artifacts` | Each entry has `id`, `type`, `name`, `location`, `status` |

---

## Lifecycle

```
created → in_progress (phases executing) → complete (all gates passed)
                    ↑                              |
                    └── compressed (token budget) ─┘
```

The packet is never deleted — it is archived when the workflow completes.