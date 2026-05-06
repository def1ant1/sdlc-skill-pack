# Skill Loading Protocol

Defines the formal process the orchestration control plane follows before
loading any domain skill. No skill loads until all checks in this protocol pass.

Referenced by `core/orchestration/SKILL.md` Step 6 (Execute and Delegate).
Enforced programmatically by `scripts/orchestration/route_skill_chain.py` and
`scripts/orchestration/validate_workflow_state.py`.

---

## Overview

Loading a skill means providing it with context, inputs, and authority to
produce outputs for its phase. It is a resource-consuming and phase-advancing
action. Loading a skill prematurely — before its dependencies are satisfied,
before its memory context is ready, or before its token budget is available —
causes incorrect output, wasted tokens, and gate failures.

This protocol runs synchronously before every skill load in a workflow.
It takes less than one reasoning step to evaluate.

---

## Protocol Steps

### Check 1 — Skill Is Known

Verify that the skill name is a recognised entry in the skill registry
(`core/orchestration/references/skill-dependency-graph.md`).

| Result | Action |
|---|---|
| Known | Continue to Check 2 |
| Unknown | Halt. Report unknown skill. Ask user to confirm intent or provide correct name. |

---

### Check 2 — Dependency Graph Satisfied

For each entry in the skill's `depends_on` list:

1. Confirm that the dependency skill appears in the active workflow's skill chain.
2. Confirm that the dependency skill's `phase_status` in the memory packet is `complete`.
3. Confirm that the dependency's phase exit gate status is `PASS` or `PASS_WITH_WARNINGS`.

| Result | Action |
|---|---|
| All dependencies complete with passing gates | Continue to Check 3 |
| Dependency present but `phase_status` not `complete` | Halt. Report which dependency is still `in_progress` or `pending`. Do not load the requested skill. |
| Dependency not in the skill chain | Halt. Add the missing dependency to the skill chain via `route_skill_chain.py`. Load the dependency first. |
| Dependency gate status is `FAIL` | Halt. Dependency gate must be re-evaluated and pass before this skill loads. Invoke gate failure protocol. |

**Exception — Standalone Skills**

Skills marked `standalone: true` in the registry may load without completed
dependencies when invoked directly by the user for a scoped single-phase
request. In this case, record in the memory packet that dependencies were not
completed, and note any assumptions the skill must make.

---

### Check 3 — Memory Packet Available

For multi-phase and full-SDLC workflows, a memory packet must exist and be
current before the skill loads.

1. Confirm `packet_id` is set and non-empty.
2. Confirm `updated_at` reflects the most recent phase completion (not stale
   from a prior session).
3. Confirm `current_phase` matches the phase of the skill being loaded.
4. Confirm `next_action.skill` matches the skill being loaded (or is being
   overridden by an explicit user instruction, which must be logged).

| Result | Action |
|---|---|
| Packet exists and is current | Continue to Check 4 |
| Packet does not exist | Create a new memory packet now. Populate `project`, `phase_status`, `constraints` from available context. Continue to Check 4. |
| Packet exists but `current_phase` mismatches | Halt. Reconcile phase mismatch with user before loading. |
| `next_action.skill` mismatches without explicit override | Surface mismatch. Confirm with user before loading a different skill than planned. |

**For single-phase requests:** Memory packet is optional. Skip this check if
no packet exists and the request is scoped to one skill.

---

### Check 4 — Required Inputs Available

Confirm that all inputs listed in the skill chain step for this skill are
available from their declared sources.

For each input in `skill_chain[step].inputs`:

| Source | Check |
|---|---|
| `user-provided` | Confirm the user has provided this artifact or information in the current conversation. If not: ask for it before loading. |
| `upstream-skill` | Confirm the artifact appears in `memory_packet.artifacts` with `status: complete` and the correct `phase`. |
| `memory-packet` | Confirm the relevant field is populated in the active memory packet. |

| Result | Action |
|---|---|
| All inputs available | Continue to Check 5 |
| Input missing from user | Ask for the missing input. Do not load the skill until it is provided. |
| Input missing from upstream skill | Upstream skill did not produce expected output. Re-run upstream skill or ask user to provide the artifact directly. |

---

### Check 5 — Token Budget

Estimate the token cost of loading and running the skill. Compare against the
remaining budget in `memory_packet.token_stats`.

**Estimation guidelines:**

| Skill Complexity | Estimated Token Cost |
|---|---|
| Simple, focused (code-review, executive-reporting) | 4K–12K tokens |
| Standard domain skill (backend, qa, devsecops) | 10K–25K tokens |
| Heavy with artifact production (architecture, ai-engineering) | 20K–40K tokens |
| Full-phase with multiple artifacts (requirements, full system design) | 15K–35K tokens |

| Result | Action |
|---|---|
| Remaining budget > estimated cost | Continue to Check 6 |
| Remaining budget < estimated cost but > compression threshold | Trigger memory compression before loading. Update `token_stats`. Then load. |
| Remaining budget < estimated cost even after compression | Halt. Inform user budget is exhausted. Options: (1) continue in a new session with the current memory packet as the starting context, (2) reduce scope of the remaining workflow. |

**Compression threshold:** `token_stats.remaining < 0.25 × token_stats.total_budget`

---

### Check 6 — No Blocking Open Questions

Confirm that the memory packet's `open_questions` list contains no open
question that blocks this skill or its phase.

For each `open_questions` entry where `blocks` matches this skill or phase:

| Result | Action |
|---|---|
| No blocking open questions | Load the skill |
| Blocking open question exists | Surface the question to the user. Do not load the skill until the question is answered and removed from `open_questions`. Record the answer in `decisions.accepted` or `decisions.pending` as appropriate. |

---

## Loading Sequence

When all six checks pass, execute in this order:

1. Set `phase_status[current_phase]` to `in_progress` in the memory packet.
2. Set `updated_at` to the current datetime.
3. Provide the skill with:
   - The `project.objective`
   - The skill's required inputs (from Check 4)
   - The relevant `decisions.accepted` and `constraints` from the memory packet
   - The quality gate criteria the skill must satisfy (from `shared/frameworks/quality-gates/catalog.md`)
   - The `gate_before_next` name so the skill knows what it is working toward
4. Execute the skill.
5. After skill completion:
   - Add all produced artifacts to `memory_packet.artifacts`.
   - Add any new decisions to `decisions.accepted` or `decisions.pending`.
   - Add any new open questions to `open_questions`.
   - Set `phase_status[current_phase]` to `complete`.
   - Evaluate the `gate_before_next` gate.
   - Update `next_action` based on gate result.
   - Update `token_stats.consumed` and `token_stats.remaining`.

---

## Protocol Failure Modes

| Failure | Symptom | Correct Action |
|---|---|---|
| Skill loaded without dependencies | Downstream skill produces output that contradicts architecture decisions not yet made | Never skip Check 2. Even standalone skills must document their assumptions. |
| Skill loaded with stale memory packet | Skill makes decisions already made or overrides prior decisions | Always verify `updated_at` reflects the current session before loading. |
| Skill loaded without required input | Skill produces output with undeclared assumptions or incomplete artifacts | Always surface missing inputs to the user before loading (Check 4). |
| Skill loaded with insufficient token budget | Context is cut off mid-skill; artifacts are incomplete | Always run Check 5. Compress before loading if near threshold. |
| Two skills loaded in parallel without explicit parallel clearance | Conflicting outputs; race condition on shared artifacts | Only load skills in parallel when they appear in a verified `execution_groups` parallel group from `route_skill_chain.py`. |

---

## Protocol Summary (Checklist Form)

Before loading any skill, confirm all six checks:

```
[ ] 1. Skill name is recognised in the skill registry
[ ] 2. All depends_on skills are complete with passing gate status
[ ] 3. Memory packet exists, is current, and phase matches
[ ] 4. All required inputs are available from declared sources
[ ] 5. Token budget is sufficient (or compression has been triggered)
[ ] 6. No open questions block this skill or phase
```

All six must be checked. A check that is not evaluated is not a pass.