# Workflow Plan Template

Canonical format for all workflow plans produced by `core/orchestration/SKILL.md`.

A Workflow Plan is required for every `multi-phase` and `full-sdlc` request.
It is produced **before** any domain skill executes and confirmed with the user
when scope is large or ambiguous.

For single-phase requests, produce only the **Phase Execution Block** (Section 3).

---

## Section 1 — Plan Header

```yaml
workflow_plan:
  plan_id:         # unique ID, format: WP-<YYYYMMDD>-<NNN>
  created:         # ISO 8601 date
  objective:       # one-sentence restatement of the user's goal
  complexity:      # single-phase | multi-phase | full-sdlc
  classification_confidence: # high | medium | low
```

**Rules:**

- `objective` must be the user's goal rephrased, not Claude's interpretation substituted for it.
- `complexity` is derived from the intent classification step — do not upgrade complexity without justification.
- `classification_confidence` below `medium` requires one clarifying question before the plan proceeds.

---

## Section 2 — Detected Phases

```yaml
  detected_phases:
    - name:          # SDLC phase name
      skill:         # primary skill for this phase
      confidence:    # high | medium | low
      rationale:     # one sentence: which signals triggered this phase
```

**Rules:**

- List phases in dependency order (upstream first).
- Include a rationale for each phase. If you cannot state why a phase was detected, remove it.
- Phases detected at `low` confidence are included but flagged for user confirmation.

---

## Section 3 — Skill Chain

```yaml
  skill_chain:
    - step: 1
      skill:          # skill name
      phase:          # SDLC phase
      depends_on:     # [] or [skill-name, ...]
      parallel_with:  # [] or [skill-name, ...] (only when graph permits)
      inputs:
        - name:       # artifact or context item name
          source:     # user-provided | upstream-skill | memory-packet
      outputs:
        - name:       # artifact name
          consumed_by: # [] or [skill-name, ...]
      gate_before_next: # quality gate name that must pass before step N+1 loads
```

**Rules:**

- `depends_on` must be consistent with `core/orchestration/references/skill-dependency-graph.md`.
- `parallel_with` is only permitted for explicitly verified parallel pairs in the dependency graph.
- `gate_before_next` must reference a gate defined in `shared/frameworks/quality-gates/`.
- The final step has no `gate_before_next`.

---

## Section 4 — Quality Gates

```yaml
  quality_gates:
    - gate_name:       # gate identifier, e.g. architecture-approved
      transition:      # "Phase A → Phase B"
      pass_criteria:
        - criterion    # concise pass condition
      fail_action:     # block | warn | escalate
      evidence_required:
        - artifact     # what must exist for gate to be evaluated
```

**Rules:**

- Every phase transition in the skill chain must have a corresponding gate entry.
- `fail_action: block` halts the workflow and requires user-acknowledged remediation.
- `fail_action: warn` surfaces the issue but does not halt — only for non-critical criteria.
- `fail_action: escalate` triggers the escalation protocol in `references/escalation-rules.md`.

---

## Section 5 — Memory Strategy

```yaml
  memory_strategy:
    preserve:
      - item          # what to keep in the memory packet across all phases
    compress_after:
      - item          # what to summarize/drop after the phase that produces it completes
    packet_location:  # path or identifier for the active memory packet
```

**Rules:**

- Always preserve: objective, accepted decisions, constraints, open questions, quality gate status.
- Always compress after phase completion: raw conversation turns, superseded drafts, intermediate reasoning.
- Never include raw transcript in the memory packet.

---

## Section 6 — Token Budget

```yaml
  token_budget:
    total_estimated:    # total token estimate for the full workflow
    allocation:
      planning:         # tokens for orchestration and workflow planning
      source_context:   # tokens for reading existing code, docs, schemas
      reasoning:        # tokens for analysis, decision-making, design
      output:           # tokens for produced artifacts and responses
      buffer:           # reserve for gate evaluation and memory operations
    compression_trigger: # % of budget consumed that triggers memory compression
```

**Token Budget Guidelines:**

| Complexity | Typical Total | Planning | Source | Reasoning | Output | Buffer |
|---|---|---|---|---|---|---|
| `single-phase` | 8K–20K | 5% | 20% | 30% | 40% | 5% |
| `multi-phase` | 20K–60K | 8% | 25% | 30% | 30% | 7% |
| `full-sdlc` | 60K–200K | 10% | 20% | 30% | 30% | 10% |

Compression trigger default: **75%** of total budget consumed.

---

## Section 7 — Risks

```yaml
  risks:
    - id:          # RISK-NNN
      description: # one-sentence risk statement
      severity:    # high | medium | low
      phase:       # which phase this risk is most relevant to
      mitigation:  # one-sentence mitigation approach
```

**Rules:**

- Include at minimum the risks inherited from the request type (check `BACKLOG.md` risk register for common patterns).
- Severity `high` risks must have an explicit mitigation before the plan is confirmed.
- Risks are carried forward in the memory packet and reviewed at each phase gate.

---

## Section 8 — Next Action

```yaml
  next_action:
    description:    # first concrete step to execute
    skill:          # which skill to load first
    input_needed:   # what the user must provide if anything is missing
    gate_to_pass:   # N/A for first step, otherwise the gate that unlocked this step
```

---

## Complete Template (Copy-Ready)

```yaml
workflow_plan:
  plan_id:
  created:
  objective:
  complexity:
  classification_confidence:

  detected_phases:
    - name:
      skill:
      confidence:
      rationale:

  skill_chain:
    - step: 1
      skill:
      phase:
      depends_on: []
      parallel_with: []
      inputs:
        - name:
          source:
      outputs:
        - name:
          consumed_by: []
      gate_before_next:

  quality_gates:
    - gate_name:
      transition:
      pass_criteria:
        -
      fail_action:
      evidence_required:
        -

  memory_strategy:
    preserve:
      -
    compress_after:
      -
    packet_location:

  token_budget:
    total_estimated:
    allocation:
      planning:
      source_context:
      reasoning:
      output:
      buffer:
    compression_trigger: 75%

  risks:
    - id:
      description:
      severity:
      phase:
      mitigation:

  next_action:
    description:
    skill:
    input_needed:
    gate_to_pass: N/A
```

---

## Rendering as Markdown

When presenting the Workflow Plan to the user, render it as structured markdown
rather than raw YAML. Use the format defined in `core/orchestration/SKILL.md`
under "Output Format — Workflow Plan". Reserve YAML for machine consumption
(scripts, memory packets, test fixtures).
