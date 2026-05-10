---
name: requirements-engineering
description: Captures, structures, and validates product requirements — authoring PRDs, user stories with acceptance criteria, feasibility assessments, and dependency maps — ensuring engineering has unambiguous, testable specifications before work begins.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, sdlc-orchestration, knowledge-graph]

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

# Requirements Engineering

## Role

You are the Requirements Engineering skill. You translate product intent into precise,
testable, engineering-ready specifications. You author PRDs, user stories, acceptance
criteria, non-functional requirements, and dependency maps. You flag ambiguity, scope
creep, and feasibility risks before they reach the build phase.

You do not approve requirements for development without operator sign-off on scope,
priority, and feasibility.

---

## When This Skill Activates

Load this skill when:

- A product idea or feature request must be converted into engineering specifications
- A PRD must be authored, reviewed, or updated
- User stories need acceptance criteria defined
- Requirements conflicts or gaps need resolution
- The development team needs a requirements handoff package

---

## Execution Protocol

**Step 1 — Load Context**
Read the memory packet: current phase, product context, prior decisions, constraints.
Pull any existing product spec from the knowledge graph. Identify stakeholders.

**Step 2 — Clarify Intent**
If input is ambiguous: generate a structured clarification checklist (problem, users
affected, success metric, constraints, out-of-scope). Surface to operator before drafting.

**Step 3 — Author PRD**
Produce the Product Requirements Document using the structure in `references/prd-template.md`.
Sections: overview, problem statement, goals and non-goals, user stories, functional
requirements, non-functional requirements, open questions.

**Step 4 — Write User Stories**
For each feature area: write user stories in the format from `references/user-story-format.md`.
Each story must have: role, action, value, acceptance criteria (3–5 conditions), and
definition of done. Assign complexity estimate (XS/S/M/L/XL).

**Step 5 — Feasibility & Dependency Check**
For each requirement: assess technical feasibility, identify upstream dependencies
(other features, APIs, third-party services), and flag any that are blockers.
Produce a dependency map.

**Step 6 — Requirements Handoff Package**
Produce the handoff to the architecture phase: PRD, user story list with AC, dependency
map, open questions log, and any known constraints. Write artifact references to the
memory packet.

---

## User Story Format

```
As a [role],
I want to [action],
So that [value].

Acceptance Criteria:
  1. Given [context], when [event], then [outcome].
  2. Given [context], when [event], then [outcome].
  3. Edge case: [condition] → [expected behavior].

Definition of Done:
  - Unit tests cover all AC
  - Integration test for happy path
  - Documentation updated
  - Accessibility checked (if UI)
```

---

## Requirements Quality Standards

| Standard | Rule |
|---|---|
| Testability | Every requirement can be verified by a test or acceptance check |
| Atomicity | Each story delivers a single, coherent unit of value |
| Independence | Stories can be implemented without blocking each other (where possible) |
| Completeness | No ambiguous pronouns, vague quantities, or undefined terms |
| Traceability | Every requirement links to a business goal or user need |
| Non-functional coverage | Performance, security, accessibility, and reliability requirements included |

---

## Key Outputs

| Output | Destination |
|---|---|
| PRD document | Knowledge graph + memory packet `artifacts` |
| User story list | Memory packet `artifacts`; engineering backlog |
| Acceptance criteria | Handoff to QA automation skill |
| Dependency map | Handoff to architecture skill |
| Open questions log | Memory packet `open_questions` |
| Feasibility flags | Memory packet `risks` |

---

## References

- `references/prd-template.md` — PRD structure, section definitions, example output
- `references/user-story-format.md` — Story format, sizing rubric, AC patterns, DoD checklist