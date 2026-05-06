# Orchestration Control Plane

Architecture reference for the SDLC Orchestration Control Plane defined in
`core/orchestration/SKILL.md`.

---

## Role

The Orchestration Control Plane is the first skill loaded for any complex,
multi-phase, or ambiguous software delivery request. It does not perform domain
work — it classifies intent, routes skill chains, enforces quality gates, and
maintains the memory packet that carries workflow state across phase transitions.

Every domain skill in the pack operates under the orchestration layer's
authority. The orchestration skill delegates; domain skills execute.

---

## When It Activates

The orchestration control plane activates when:

- The request spans more than one SDLC phase
- The user asks for an end-to-end plan, roadmap, or full workflow
- The user's intent is ambiguous and must be classified before work begins
- A phase handoff is required and a memory packet must be created or updated

Single-phase, well-scoped requests load the target domain skill directly
without routing through the control plane.

---

## Architecture Overview

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│           SDLC Orchestration Control Plane           │
│                                                     │
│  Step 1: Intent Classification                      │
│    └─ intent-classification.md                      │
│                                                     │
│  Step 2: Skill Chain Routing                        │
│    └─ skill-dependency-graph.md                     │
│    └─ route_skill_chain.py                          │
│                                                     │
│  Step 3: Workflow Plan Production                   │
│    └─ workflow-plan-template.md                     │
│    └─ plan_workflow.py                              │
│                                                     │
│  Step 4: Quality Gate Enforcement                   │
│    └─ quality-gates/catalog.md                     │
│    └─ gate-failure-handling.md                      │
│    └─ validate_workflow_state.py                    │
│                                                     │
│  Step 5: Memory Packet Management                   │
│    └─ memory-packet-schema.md                       │
│    └─ core/memory-token-management/                 │
│                                                     │
│  Step 6: Skill Delegation                           │
│    └─ skill-loading-protocol.md                     │
└─────────────────────────────────────────────────────┘
     │
     ▼
Domain Skill (e.g. system-architecture, backend-engineering)
     │
     ▼
Phase Output → Gate Evaluation → Memory Packet Update → Next Skill
```

---

## Step 1 — Intent Classification

The classifier maps natural-language signals to SDLC phases using the rules in
`core/orchestration/references/intent-classification.md`.

### How It Works

1. The objective is tokenised and matched against 13 phase rule sets.
2. Each rule set has **primary signals** (strong matches), **supporting signals**
   (weaker matches), and **negative signals** (reduce confidence).
3. A confidence level (`high`, `medium`, `low`) is assigned per phase.
4. All matching phases are collected; requests matching two or more phases are
   classified as `multi-phase` or `full-sdlc`.
5. If no phase matches with meaningful confidence, the request is classified as
   `unknown` and one clarifying question is asked.

### Implemented In

- Prompt layer: `core/orchestration/references/intent-classification.md`
- Script layer: `scripts/orchestration/plan_workflow.py` (`classify_intent()`)

### Extending the Classifier

To add a new phase or improve signal coverage:

1. Add or update the rule entry in `intent-classification.md` (primary,
   supporting, negative signals; confidence mapping; upstream/downstream).
2. Add the corresponding rule tuple to `_CLASSIFICATION_RULES` in
   `plan_workflow.py`.
3. Add the phase to `_PHASE_ORDER` in `plan_workflow.py` at the correct
   position in the lifecycle.
4. Add benchmark prompts for the new phase to
   `tests/fixtures/orchestration-prompts.json`.
5. Run the regression suite: `pytest tests/orchestration/`.
6. Verify classification accuracy remains above 90%.

---

## Step 2 — Skill Chain Routing

After classification, the dependency graph resolves the minimum ordered skill
chain needed to satisfy all detected phases.

### How It Works

1. Detected skill names are passed to `route_skill_chain.py`.
2. Missing dependencies are added automatically (e.g. requesting
   `backend-engineering` adds `system-architecture`).
3. A topological sort (Kahn's algorithm) produces the dependency-ordered chain.
4. Parallel execution groups are identified from the graph's explicit
   `parallel_with` declarations.
5. Each step in the chain is annotated with its `gate_before_next` — the quality
   gate name that must pass before the next step loads.

### Dependency Graph

The full graph lives in
`core/orchestration/references/skill-dependency-graph.md`. Key structural rules:

- `system-architecture` is the primary unblocking skill — most downstream skills
  depend on it.
- `release-management` requires both `qa-automation` and `devsecops` to be
  complete.
- `executive-reporting` and `code-review` are standalone — they load without
  requiring prior phases to complete.
- Parallel execution is only permitted for explicitly declared pairs (e.g.
  `devsecops` ‖ `qa-automation`, `ai-engineering` ‖ `backend-engineering`).

### Extending the Dependency Graph

To add a new skill:

1. Add its entry to `SKILLS` in `route_skill_chain.py` with `depends_on`,
   `parallel_with`, `standalone`, and `gate_before_next`.
2. Update `core/orchestration/references/skill-dependency-graph.md` with the
   full per-skill table.
3. Update `docs/architecture/skill-dependency-graph.md` with the artifact flow row.
4. Add the skill to `_PHASE_DEPS` in `validate_workflow_state.py`.
5. Run `pytest tests/orchestration/` — pay attention to ordering invariants in
   `test_orchestration_regression.py::TestRouteRegressionInvariants`.

---

## Step 3 — Workflow Plan Production

For multi-phase and full-SDLC requests, the control plane produces a Workflow
Plan before any domain skill executes.

### Plan Contents

| Field | Description |
|---|---|
| `plan_id` | Unique identifier (`WP-YYYYMMDD-NNN`) |
| `objective` | User's goal verbatim |
| `complexity` | `single-phase` / `multi-phase` / `full-sdlc` |
| `detected_phases` | Phase list with confidence and rationale |
| `skill_chain` | Ordered steps with inputs, outputs, gate annotations |
| `execution_groups` | Parallel groupings |
| `quality_gates` | Gate name, transition, and fail action per transition |
| `memory_strategy` | What to preserve and what to compress |
| `token_budget` | Tier-calibrated allocation across planning/source/reasoning/output/buffer |
| `next_action` | First concrete step |

### Plan Confirmation

Get user confirmation before executing when:

- Complexity is `full-sdlc` and scope is large
- Any detected phase has `confidence: low`
- Dependency additions significantly expand the requested scope

### Implemented In

- Template: `core/orchestration/references/workflow-plan-template.md`
- Script: `scripts/orchestration/plan_workflow.py` (`plan()`)

---

## Step 4 — Quality Gate Enforcement

Every phase transition is gated. The control plane evaluates the exit gate for
the current phase before loading the next skill.

### Gate Lifecycle

```
Phase N executing
      │
      ▼ (skill signals completion)
Collect evidence (artifacts from memory packet)
      │
      ▼
Evaluate criteria → PASS / PASS_WITH_WARNINGS / FAIL
      │
   ┌──┴──┐
PASS    FAIL
  │       │
  ▼       ▼
Load    Gate failure protocol:
next      1. Surface all failures
skill     2. Generate REM-NNN tasks
          3. Block next phase
          4. Await user confirmation
          5. Re-evaluate
          6. Escalate on second failure
```

### Gate Catalog

Eight gates cover the full SDLC lifecycle:

| Gate | Transition |
|---|---|
| `requirements-complete` | Requirements → Architecture |
| `architecture-approved` | Architecture → Backend / AI / Frontend |
| `ai-design-approved` | AI Engineering → Backend |
| `backend-implementation-ready` | Backend → DevSecOps |
| `security-review-passed` | DevSecOps → QA |
| `test-strategy-accepted` | QA → Release |
| `release-readiness-confirmed` | Release → Observability |
| `operations-readiness-confirmed` | Observability → SRE |

Full criteria for each gate: `shared/frameworks/quality-gates/catalog.md`

Failure handling: `core/orchestration/references/gate-failure-handling.md`

Programmatic enforcement: `scripts/orchestration/validate_workflow_state.py`

---

## Step 5 — Memory Packet Management

The memory packet is the single source of truth for workflow state across phase
transitions. It replaces raw conversation history as the inter-phase context
carrier.

### Packet Fields

| Section | Purpose |
|---|---|
| Identity (`packet_id`, `version`, timestamps) | Uniqueness and staleness detection |
| `project` | Objective, domain, complexity |
| `phase_status` | Per-phase lifecycle status |
| `decisions` | Accepted, rejected, and pending decisions with rationale |
| `constraints` | Business, technical, security, compliance, AI-specific |
| `artifacts` | Produced artifacts with type, location, and consumer list |
| `quality_gate_status` | Gate evaluation history (all records retained) |
| `open_questions` | Unresolved questions blocking phase advancement |
| `risks` | Active risks with severity and mitigation status |
| `token_stats` | Running budget consumption and compression state |
| `next_action` | Current execution pointer |

### Handoff Protocol

When handing off to a downstream skill, load only the sections it needs:
- Always: `project`, `current_phase`, `constraints`, `decisions.accepted`, `next_action`
- Conditionally: latest gate result, artifacts filtered to `consumed_by` the skill

Do not load the full packet into context when a subset satisfies the skill's
input requirements.

### Compression

When `token_stats.consumed` reaches 75% of `token_stats.total_budget`:

1. Trigger compression via `core/memory-token-management/SKILL.md`.
2. Preserve all required fields (decisions, constraints, gate status, artifacts,
   open questions, risks, next action).
3. Drop raw conversation turns, superseded drafts, and intermediate reasoning.
4. Update `token_stats.compression_triggered = true`.

Schema: `docs/schemas/memory-packet-schema.md`

Validation: `scripts/orchestration/validate_workflow_state.py`

---

## Step 6 — Skill Loading Protocol

Before every skill load, six checks must pass:

| Check | Condition |
|---|---|
| 1. Registry | Skill name is recognised |
| 2. Dependencies | All `depends_on` skills are `complete` with passing gates |
| 3. Memory packet | Packet exists, is current, phase matches |
| 4. Inputs | All required inputs are available from declared sources |
| 5. Token budget | Sufficient budget remains (or compression is triggered first) |
| 6. Open questions | No blocking open questions for this skill or phase |

Full protocol: `core/orchestration/references/skill-loading-protocol.md`

---

## Escalation

The control plane escalates to human review when:

- A quality gate fails twice on the same criterion after remediation
- A security gate fails at `critical` severity
- The workflow involves regulated data (PII, PHI, financial)
- AI risk classification is `high` or `critical`
- The user requests an explicit waiver on a blocking gate criterion

Escalation protocol: `core/orchestration/references/escalation-rules.md`

---

## Scripts Reference

| Script | Purpose |
|---|---|
| `scripts/orchestration/plan_workflow.py` | Classify intent → produce Workflow Plan JSON |
| `scripts/orchestration/route_skill_chain.py` | Route ordered skill chain from detected phases |
| `scripts/orchestration/validate_workflow_state.py` | Validate memory packet for phase transition readiness |

---

## Tests Reference

| Test File | Coverage |
|---|---|
| `tests/orchestration/test_plan_workflow.py` | Intent classification, schema, complexity, gates |
| `tests/orchestration/test_route_skill_chain.py` | Routing, dependency order, parallel groups, unknowns |
| `tests/orchestration/test_validate_workflow_state.py` | Required fields, dependency order, gate blocking, artifacts |
| `tests/orchestration/test_orchestration_regression.py` | Full pipeline integration, benchmark accuracy (>90%), ordering invariants |
| `tests/fixtures/orchestration-prompts.json` | 30 benchmark prompts across all SDLC phases |

---

## How to Extend Routing Logic

A new contributor extending routing logic should follow this sequence:

1. **Add the phase to the classifier** (`intent-classification.md` and
   `plan_workflow.py::_CLASSIFICATION_RULES`) with primary, supporting, and
   negative signals.

2. **Add the skill to the dependency graph** (`route_skill_chain.py::SKILLS`,
   `skill-dependency-graph.md`, `validate_workflow_state.py::_PHASE_DEPS`).

3. **Define the exit gate** in `shared/frameworks/quality-gates/catalog.md` and
   register the gate-to-phase mapping in
   `validate_workflow_state.py::_GATE_TO_TARGET_PHASE`.

4. **Add benchmark prompts** to `tests/fixtures/orchestration-prompts.json`
   covering single-phase, multi-phase, and ambiguous variants.

5. **Run the full test suite** and confirm:
   - Classification accuracy remains above 90%
   - All dependency ordering invariants pass
   - Validate catches gate violations for the new phase

6. **Create the SKILL.md** for the new domain skill using the generator:
   `python scripts/generators/create_skill.py <skill-name>`