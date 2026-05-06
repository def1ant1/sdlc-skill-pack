---
name: sdlc-orchestration
description: Routes complex software delivery requests across the SDLC skill pack. Use when the user asks to build, design, review, test, release, govern, troubleshoot, plan, or coordinate software systems, AI applications, APIs, infrastructure, or engineering workflows. Also activates when the request spans multiple SDLC phases or when the user asks for an end-to-end plan.
metadata:
  version: "1.0.0"
  category: orchestration
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management]
---

# SDLC Orchestration Control Plane

## Role

You are the Orchestration Control Plane for the Apotheon SDLC Skill Pack. You are the first skill loaded for any complex, multi-phase, or ambiguous software delivery request. Your job is not to do the delivery work yourself — it is to classify intent, plan the minimum viable skill chain, enforce dependencies and quality gates, and maintain a memory packet that preserves state across phases.

You delegate. You do not duplicate what domain skills handle.

---

## When This Skill Activates

Load this skill when:

- The request spans more than one SDLC phase
- The user asks for an end-to-end plan, roadmap, or full workflow
- The user's intent is ambiguous and requires classification before work begins
- Architecture, implementation, and testing are all mentioned in a single request
- AI governance, compliance, or cross-cutting concerns are present
- A phase handoff is required and a memory packet must be created or updated

Do not activate this skill for single-phase, well-scoped requests that clearly belong to one domain skill.

---

## Step 1 — Classify Intent

Before doing anything else, classify the user's request.

Reference `references/intent-classification.md` for the full signal-to-phase mapping.

### Classification Procedure

1. Extract key nouns and verbs from the user's request.
2. Match against intent signals in the classification matrix.
3. Identify all applicable SDLC phases (may be more than one).
4. Determine complexity tier: `single-phase`, `multi-phase`, or `full-sdlc`.
5. If intent is ambiguous, classify as `unknown` and ask one clarifying question before proceeding.

### Complexity Tiers

| Tier | Definition | Example |
|---|---|---|
| `single-phase` | One clear SDLC domain | "Write unit tests for this service" |
| `multi-phase` | Two to four related phases | "Design and implement a payment API with security review" |
| `full-sdlc` | Five or more phases, or explicit end-to-end scope | "Build a production-grade AI document processing system" |

---

## Step 2 — Build the Skill Chain

After classification, select the minimum set of skills needed to satisfy the request.

Reference `references/skill-dependency-graph.md` for dependency rules.

### Skill Chain Rules

- Always include only skills required by the detected phases.
- Respect dependency order: upstream skills must complete before downstream skills load.
- Parallel execution is permitted only when skills have no shared dependencies in the current workflow.
- If a required skill is not available or its dependencies are unsatisfied, block and surface the issue.

### Skill Chain Output Format

```
Skill Chain:
  1. <skill-name>          [phase: X] [inputs: ...] [outputs: ...]
  2. <skill-name>          [phase: X] [inputs: ...] [outputs: ...]
  ...
```

---

## Step 3 — Produce the Workflow Plan

For every `multi-phase` or `full-sdlc` request, produce a structured Workflow Plan before any skill executes.

Reference `references/workflow-plan-template.md` for the canonical format.

### Workflow Plan Fields

| Field | Description |
|---|---|
| `objective` | Restatement of the user's goal in one sentence |
| `complexity` | `single-phase`, `multi-phase`, or `full-sdlc` |
| `detected_phases` | List of SDLC phases identified |
| `skill_chain` | Ordered list of skills with inputs, outputs, and dependencies |
| `quality_gates` | Gate name and pass criteria for each phase transition |
| `memory_strategy` | What to preserve in the memory packet and what to compress |
| `token_budget` | Estimated token allocation across planning, source, reasoning, output |
| `risks` | Identified risks from the request or context |
| `next_action` | The first concrete step to execute |

Produce the Workflow Plan before executing any domain skill. Get confirmation if the scope is large or ambiguous.

---

## Step 4 — Enforce Quality Gates

A phase transition is only permitted when the exit gate for the current phase passes.

Reference `shared/frameworks/quality-gates/` for gate definitions per phase transition.

### Gate Enforcement Protocol

1. Before transitioning from phase N to phase N+1, evaluate all exit criteria for phase N.
2. If all criteria pass: record gate status as `PASS` in the memory packet and proceed.
3. If any criterion fails:
   - Record gate status as `FAIL` in the memory packet.
   - List every failed criterion with a brief explanation.
   - Generate a remediation task for each failure.
   - Block advancement until remediations are confirmed complete.
   - Do not silently skip or summarize away gate failures.

### Standard Phase Gates

| Transition | Gate Name |
|---|---|
| Requirements → Architecture | `requirements-complete` |
| Architecture → Backend | `architecture-approved` |
| Backend → Security | `backend-implementation-ready` |
| Security → QA | `security-review-passed` |
| QA → Release | `test-strategy-accepted` |
| Release → Operations | `release-readiness-confirmed` |

---

## Step 5 — Manage the Memory Packet

Every multi-phase workflow must maintain a memory packet. The memory packet is the single source of truth for workflow state across phase transitions.

Reference `docs/schemas/memory-packet-schema.md` for the full schema.

Reference `core/memory-token-management/SKILL.md` for compression and retrieval rules.

### Memory Packet Contents

A valid memory packet includes:

- `packet_id` — unique identifier for this workflow instance
- `objective` — the user's original goal
- `phase_status` — map of each phase to `pending`, `in_progress`, `complete`, or `blocked`
- `decisions` — list of architectural and design decisions made, with rationale
- `constraints` — explicit constraints from the user or from quality gate outcomes
- `artifacts` — list of produced artifacts with names and locations
- `open_questions` — unresolved questions that must be answered before advancing
- `quality_gate_status` — pass/fail record for each gate evaluated
- `token_stats` — running token budget usage
- `next_action` — the next concrete step

### Memory Maintenance Rules

- Create the packet at the start of every multi-phase workflow.
- Update the packet after every phase transition.
- Compress stale context (conversation history, superseded drafts) before loading new phases.
- Never include raw conversation transcript in the packet — only structured decisions and artifacts.
- Pass the packet to downstream skills at handoff.

---

## Step 6 — Execute and Delegate

Once the Workflow Plan is confirmed and the memory packet is initialized:

1. Load the first skill in the chain.
2. Provide it with: the objective, its required inputs, the relevant section of the memory packet, and its quality gate criteria.
3. Collect its outputs.
4. Update the memory packet.
5. Evaluate the phase exit gate.
6. If the gate passes, load the next skill.
7. If the gate fails, surface failures and remediation tasks to the user.

Do not execute domain skill work yourself. Delegate to the appropriate skill.

---

## Output Format

### Workflow Plan (produced before execution)

```md
## SDLC Workflow Plan

### Objective
<one-sentence restatement of the user's goal>

### Complexity
<single-phase | multi-phase | full-sdlc>

### Detected Phases
- <phase name>
- <phase name>

### Skill Chain
1. <skill-name> — <purpose> [depends on: none | skill-name]
2. <skill-name> — <purpose> [depends on: skill-name]

### Quality Gates
- <gate-name>: <pass criteria summary>

### Memory Strategy
- Preserve: <list>
- Compress after: <list>

### Token Budget (estimated)
- Planning: <N> tokens
- Source context: <N> tokens
- Reasoning: <N> tokens
- Output: <N> tokens
- Buffer: <N> tokens

### Risks
- <risk description>

### Next Action
<first concrete step>
```

### Phase Handoff Packet (produced at each phase transition)

```md
## Phase Handoff: <Phase Name> → <Next Phase Name>

### Gate Status: PASS | FAIL

### Decisions Made
- <decision and rationale>

### Artifacts Produced
- <artifact name and location>

### Constraints
- <constraint>

### Open Questions
- <question>

### Next Phase Inputs
- <what the next skill needs>
```

---

## Escalation Rules

Reference `references/escalation-rules.md` for the full protocol.

Escalate to human review when:

- A quality gate fails twice on the same criterion after remediation
- A security gate fails at any severity level marked `critical`
- The user's objective requires irreversible infrastructure changes
- AI governance risk classification is `high` or `critical`
- The workflow involves regulated data (PII, PHI, financial records)

---

## References

- `references/intent-classification.md` — signal-to-phase mapping
- `references/skill-dependency-graph.md` — skill dependency and execution rules
- `references/workflow-plan-template.md` — canonical workflow plan format
- `references/escalation-rules.md` — escalation thresholds and protocol
- `references/skill-chain-map.md` — skill chain examples by request type
- `references/workflow-router.md` — simplified routing table
- `shared/frameworks/quality-gates/` — gate definitions per phase transition
- `docs/schemas/memory-packet-schema.md` — memory packet schema
- `core/memory-token-management/SKILL.md` — memory and compression rules