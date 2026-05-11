# Skill Dependency Graph — Architecture Reference

This document is the architecture-level view of the SDLC skill dependency graph.
For the operational reference used by the orchestration control plane, see
`core/orchestration/references/skill-dependency-graph.md`.

---

## Purpose

The skill dependency graph defines the valid ordering and parallelism rules for
all 13 domain skills in the SDLC skill pack. The orchestration control plane
enforces this graph when building skill chains for any multi-phase or full-SDLC
workflow.

---

## Design Principles

**1. Upstream outputs gate downstream inputs.**
No skill may load until all required upstream outputs exist in the memory packet
or are provided directly by the user.

**2. Dependency order reflects artifact flow, not time.**
Dependencies are not arbitrary sequencing rules — they reflect which skills
produce artifacts that other skills consume. The graph evolves as skill output
schemas evolve.

**3. Parallel execution is bounded by the graph.**
Two skills may run in parallel only when neither depends on the other's outputs
in the current workflow. This is explicitly enumerated; parallelism is never
assumed.

**4. Standalone skills are exceptions, not the default.**
A skill is standalone only when it can produce useful output without prior-phase
artifacts. This is explicitly noted in the graph, not inferred.

**5. The graph is enforced, not advisory.**
The orchestration control plane blocks dependency violations. Skills do not
self-assess their own dependency state.

---

## Phase Sequence (Default Full-SDLC Order)

```
Phase 1:  requirements-engineering
Phase 2:  system-architecture
Phase 3:  ai-engineering           (when AI is in scope)
          backend-engineering      (parallel with ai-engineering when services are independent)
Phase 4:  frontend-engineering     (when UI is in scope)
          devsecops                (can begin when architecture is complete)
Phase 5:  qa-automation
          code-review              (can run in parallel with QA)
Phase 6:  release-management
Phase 7:  observability
Phase 8:  sre-incident-response    (post-deployment)
          compliance-governance    (can run parallel with release when security/QA gates pass)
Phase 9:  executive-reporting      (read-only, any time)
```

---

## Artifact Flow Summary

| Upstream Skill | Key Outputs | Consumed By |
|---|---|---|
| `requirements-engineering` | PRD, user stories, acceptance criteria, traceability matrix | `system-architecture`, `qa-automation` |
| `system-architecture` | ADRs, service boundary map, data model, NFRs | `backend-engineering`, `ai-engineering`, `frontend-engineering`, `devsecops` |
| `ai-engineering` | AI architecture, eval plan, risk classification, model design | `backend-engineering`, `devsecops`, `qa-automation`, `compliance-governance` |
| `backend-engineering` | API specs, service plans, database schema, implementation tasks | `frontend-engineering`, `devsecops`, `qa-automation` |
| `frontend-engineering` | Component design, accessibility report, implementation plan | `qa-automation`, `code-review` |
| `devsecops` | Threat model, security findings, remediation tasks, security gate status | `qa-automation`, `release-management`, `compliance-governance` |
| `qa-automation` | Test strategy, test cases, coverage plan, regression baseline | `release-management`, `compliance-governance` |
| `code-review` | Review findings, severity ratings, refactor recommendations | `devsecops` (if security issues found), `qa-automation` (if test gaps found) |
| `release-management` | Release checklist, deployment plan, rollback plan, changelog | `observability` |
| `observability` | SLO definitions, alert strategy, dashboard requirements | `sre-incident-response` |
| `sre-incident-response` | Incident runbook, postmortem, remediation backlog | `executive-reporting` |
| `compliance-governance` | Governance review, compliance checklist, audit evidence | `executive-reporting` |
| `executive-reporting` | Executive summary, risk summary, roadmap status | none |

---

## Extension Guidelines

When adding a new skill to the pack:

1. Define its `depends_on` list — which skills must produce outputs before this skill can load.
2. Define its `enables` list — which downstream skills consume its outputs.
3. Define whether it is `standalone` and under what conditions.
4. Update `core/orchestration/references/skill-dependency-graph.md` with the new node.
5. Update the intent classification matrix if the skill covers a new phase or intent signal.
6. Update the quality gate catalog if a new phase transition gate is required.
7. Run `pytest` to verify no existing tests break.

---

## Related Documents

- `core/orchestration/references/skill-dependency-graph.md` — operational graph with full per-skill tables
- `core/orchestration/references/intent-classification.md` — maps user signals to phases
- `core/orchestration/references/skill-chain-map.md` — example chains by request type
- `shared/frameworks/quality-gates/` — gate definitions per phase transition
- `docs/schemas/memory-packet-schema.md` — how dependency state is tracked across phases

---

## Skill Graph Engine MVP (MB-P0-004)

The runtime now includes `core/skill-graph-engine/engine.py`, which produces a planner-consumable graph containing:

- Skill/agent/core nodes.
- Dependency edges.
- Optional metadata edges for tools, policies, connectors, and memory requirements.
- Diagnostics for missing dependencies, dependency cycles, and routing collisions.

Planner integration surface:

- `scripts/skills/build_skill_graph.py` writes `reports/skill_graph.json|md|mmd`.
- `scripts/skills/resolve_skill_dependencies.py <intent> [--required ...]` returns candidate skills sorted by missing dependency risk.
- `SkillGraphEngine.query_candidates(intent, required=None)` is the programmatic interface for orchestration planners.
