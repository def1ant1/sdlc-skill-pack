# Retrieval Priorities

Used by `core/memory-token-management/SKILL.md` to define per-skill context loading rules
and the canonical priority order for retrieving memory packet sections.

---

## Global Priority Order

When selecting what to load into context for any skill, apply this order:

| Priority | Item | Load Condition |
|---|---|---|
| 1 | Latest user instruction | Always |
| 2 | `current_phase` + `next_action` | Always |
| 3 | `project.objective` + `project.complexity` | Always |
| 4 | `decisions.accepted` | Always |
| 5 | `constraints` (all categories) | Always |
| 6 | `open_questions` (blocking current phase) | If any exist |
| 7 | `quality_gate_status` (current gate only) | On gate transition |
| 8 | `artifacts` (consumed_by current skill) | On skill load |
| 9 | `risks` (high + critical) | Always |
| 10 | `phase_status` (full map) | On handoff only |
| 11 | External source files | On demand, lazy |
| 12 | Historical phase outputs | Only if referenced by current step |

---

## Per-Skill Retrieval Rules

| Skill | Must Load | Do Not Load |
|---|---|---|
| requirements-engineering | objective, constraints, open_questions | Backend artifacts, test results |
| system-architecture | decisions.accepted, constraints, requirements artifacts | QA results, deployment configs |
| ai-engineering | architecture artifacts, ai_specific constraints, decisions | Frontend code, release notes |
| backend-engineering | architecture artifacts, API contracts, decisions | Frontend components, marketing |
| frontend-engineering | architecture artifacts, API contracts, backend artifacts | Security scan details |
| devsecops | all constraints (security), architecture artifacts | GTM artifacts, reporting |
| qa-automation | backend artifacts, test strategy, acceptance criteria | Architecture decisions (full) |
| release-management | qa artifacts, security gate status, release notes | Requirements history |
| observability | release artifacts, SLO definitions | Requirements, architecture decisions |
| sre-incident-response | observability artifacts, runbooks, SLO status | GTM, reporting |
| compliance-governance | all constraints, security artifacts, gate history | Frontend components |
| executive-reporting | phase_status (all), risks, decisions.accepted | Raw code, test output |
| code-review | backend/frontend artifacts (code only) | GTM, compliance details |

---

## Lazy Loading Rules

Apply these rules to avoid loading unnecessary context:

1. **Section-first**: Load the table of contents or heading list of a document before
   loading its full content. Only load sections explicitly needed.

2. **On-demand**: Do not preload source files — load them only when a skill step
   explicitly references them.

3. **Recency bias**: When multiple versions of an artifact exist, load only the most
   recent `status: final` version.

4. **Deduplicate**: If the same content would be loaded from two sources, load it once
   and reference the canonical location.

5. **No speculative loading**: Do not load artifacts for a phase that hasn't started yet.
   Load only for the `current_phase`.