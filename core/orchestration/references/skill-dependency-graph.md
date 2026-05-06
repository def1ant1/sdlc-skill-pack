# Skill Dependency Graph

Used by `core/orchestration/SKILL.md` Step 2 to enforce dependency order when building skill chains.

---

## Graph Overview

```
requirements-engineering
        │
        ▼
system-architecture ◄──────────────────────────────────┐
        │                                               │
        ├──────────────────┐          (architecture     │
        ▼                  ▼           is optional for  │
ai-engineering     backend-engineering  code-review)    │
        │                  │                            │
        │                  ├──────────────────────┐     │
        │                  ▼                      ▼     │
        │          frontend-engineering      code-review─┘
        │                  │
        ├──────────────────┤
        ▼                  ▼
   devsecops ◄─────────────┘
        │
        ▼
  qa-automation
        │
        ▼
release-management
        │
        ▼
  observability
        │
        ▼
sre-incident-response
        │
        ▼
 executive-reporting ◄── compliance-governance ◄── devsecops + qa-automation
```

---

## Dependency Table

Each skill lists its required upstream skills (`depends_on`) and the skills it enables (`enables`).

### requirements-engineering

| Field | Value |
|---|---|
| **Skill** | `requirements-engineering` |
| **Phase** | Requirements |
| **Depends On** | none |
| **Enables** | `system-architecture`, `qa-automation` (acceptance criteria), `executive-reporting` |
| **Parallel With** | none |
| **Standalone** | yes — can run without any upstream skill |
| **Notes** | First skill in any full-SDLC chain. Outputs feed the architecture decision process and QA traceability. |

---

### system-architecture

| Field | Value |
|---|---|
| **Skill** | `system-architecture` |
| **Phase** | Architecture |
| **Depends On** | `requirements-engineering` (preferred) or user-provided scope |
| **Enables** | `backend-engineering`, `ai-engineering`, `frontend-engineering`, `devsecops` (threat modeling requires architecture) |
| **Parallel With** | none (is the primary unblocking skill) |
| **Standalone** | yes — can run against a brief or context without formal requirements |
| **Notes** | ADRs produced here are consumed by all downstream skills. If requirements are skipped, architecture assumptions must be documented in the memory packet. |

---

### ai-engineering

| Field | Value |
|---|---|
| **Skill** | `ai-engineering` |
| **Phase** | AI Engineering |
| **Depends On** | `system-architecture` |
| **Enables** | `backend-engineering` (AI service integration), `devsecops` (AI-specific threat model), `qa-automation` (eval harness), `compliance-governance` (AI risk classification) |
| **Parallel With** | `frontend-engineering` (when AI backend is independently specified) |
| **Standalone** | no — requires architecture context to produce safe AI design |
| **Notes** | Must produce an AI risk classification before `devsecops` and `compliance-governance` can complete their AI-related work. |

---

### backend-engineering

| Field | Value |
|---|---|
| **Skill** | `backend-engineering` |
| **Phase** | Backend |
| **Depends On** | `system-architecture` |
| **Enables** | `frontend-engineering`, `devsecops`, `qa-automation`, `release-management` |
| **Parallel With** | `ai-engineering` (when AI and backend are separate service concerns) |
| **Standalone** | no — service boundaries must be defined by architecture first |
| **Notes** | API contracts produced here are consumed by frontend and QA. Must be complete before security review. |

---

### frontend-engineering

| Field | Value |
|---|---|
| **Skill** | `frontend-engineering` |
| **Phase** | Frontend |
| **Depends On** | `system-architecture`, `backend-engineering` (API contracts) |
| **Enables** | `qa-automation` (UI test cases), `code-review` |
| **Parallel With** | `ai-engineering` (if frontend has no AI dependency) |
| **Standalone** | no — requires API contracts from backend |
| **Notes** | Can begin in parallel with backend when a stable API contract is available (mocked or designed). |

---

### devsecops

| Field | Value |
|---|---|
| **Skill** | `devsecops` |
| **Phase** | Security |
| **Depends On** | `system-architecture` (minimum), `backend-engineering` (preferred) |
| **Enables** | `qa-automation` (security test cases), `release-management` (security gate), `compliance-governance` |
| **Parallel With** | `qa-automation` (functional tests can proceed while security review runs in parallel if backend is complete) |
| **Standalone** | no — threat modeling requires a system design to threat model |
| **Notes** | Security review of AI systems additionally requires `ai-engineering` output. Threat model must reference architecture ADRs. |

---

### qa-automation

| Field | Value |
|---|---|
| **Skill** | `qa-automation` |
| **Phase** | QA |
| **Depends On** | `backend-engineering` or `frontend-engineering` (at least one implementation artifact required) |
| **Enables** | `release-management`, `compliance-governance` (test evidence) |
| **Parallel With** | `devsecops` (when backend is complete and security review does not block test design) |
| **Standalone** | partial — test strategy can be written against requirements; test execution requires implementation |
| **Notes** | Can begin test strategy and case design as soon as requirements and architecture exist. Execution depends on implementation. |

---

### code-review

| Field | Value |
|---|---|
| **Skill** | `code-review` |
| **Phase** | Code Review |
| **Depends On** | code artifact (can be provided directly by user without formal upstream skills) |
| **Enables** | `devsecops` (when security issues found), `qa-automation` (when test gaps found) |
| **Parallel With** | `devsecops`, `qa-automation` |
| **Standalone** | yes — most commonly run as a standalone single-phase review |
| **Notes** | Standalone by design. When used in a full-SDLC chain, runs after backend or frontend engineering to validate implementation against architectural intent. |

---

### release-management

| Field | Value |
|---|---|
| **Skill** | `release-management` |
| **Phase** | Release |
| **Depends On** | `qa-automation` (test strategy passed), `devsecops` (security gate passed) |
| **Enables** | `observability`, `executive-reporting` |
| **Parallel With** | none — release readiness requires QA and security gates to pass first |
| **Standalone** | no — cannot assess release readiness without upstream gate results |
| **Notes** | Release plan must reference QA coverage results and security gate status from the memory packet. |

---

### observability

| Field | Value |
|---|---|
| **Skill** | `observability` |
| **Phase** | Observability |
| **Depends On** | `release-management` (deployment exists or is planned) |
| **Enables** | `sre-incident-response` |
| **Parallel With** | none |
| **Standalone** | partial — SLO and alert strategy can be designed pre-release; dashboards require a running system |
| **Notes** | Observability design should be planned as part of release. Instrumentation review requires a deployed artifact. |

---

### sre-incident-response

| Field | Value |
|---|---|
| **Skill** | `sre-incident-response` |
| **Phase** | Operations |
| **Depends On** | `observability` |
| **Enables** | `executive-reporting` |
| **Parallel With** | none |
| **Standalone** | yes — can triage and postmortem an active incident without completing prior phases |
| **Notes** | For active incident response, this skill loads immediately regardless of other phase state. Post-incident work feeds back into architecture and QA. |

---

### compliance-governance

| Field | Value |
|---|---|
| **Skill** | `compliance-governance` |
| **Phase** | Compliance |
| **Depends On** | `devsecops`, `qa-automation` |
| **Enables** | `executive-reporting` |
| **Parallel With** | `release-management` (compliance review and release prep can run in parallel when security and QA gates are already passed) |
| **Standalone** | partial — policy mapping can run early; audit evidence requires implementation artifacts |
| **Notes** | For AI systems, additionally depends on `ai-engineering` AI risk classification output. |

---

### executive-reporting

| Field | Value |
|---|---|
| **Skill** | `executive-reporting` |
| **Phase** | Reporting |
| **Depends On** | any completed phase (reports on current workflow state) |
| **Enables** | none |
| **Parallel With** | any phase (reporting is always a read-only summary) |
| **Standalone** | yes — can produce a status report against any available memory packet |
| **Notes** | Reads from the memory packet. Does not advance the workflow. |

---

## Parallel Execution Rules

Two skills may execute in parallel within the same workflow when **both** of the following are true:

1. Neither skill is listed as a `depends_on` for the other in this graph.
2. Neither skill requires an artifact that the other skill is currently producing.

### Verified Parallel Pairs

| Pair | Condition |
|---|---|
| `backend-engineering` + `ai-engineering` | When AI and backend are separate service boundaries |
| `frontend-engineering` + `ai-engineering` | When frontend has no AI-direct dependency |
| `devsecops` + `qa-automation` | When backend implementation is complete |
| `release-management` + `compliance-governance` | When security and QA gates have already passed |
| `executive-reporting` + any phase | Reporting is always read-only |

---

## Standalone Skills

These skills can be loaded without requiring any upstream skills to have run first:

| Skill | Condition for Standalone Use |
|---|---|
| `requirements-engineering` | Always — it is the origin phase |
| `system-architecture` | When user provides scope or brief directly |
| `code-review` | When user provides code directly |
| `sre-incident-response` | When an active incident requires immediate triage |
| `executive-reporting` | When user requests a status summary against any context |

---

## Dependency Violation Rules

The orchestration control plane must enforce these rules. A dependency violation occurs when:

- A downstream skill is loaded before its `depends_on` skills have produced their required outputs.
- A phase gate fails but the next skill is loaded anyway.
- A skill is run in parallel with a skill it depends on.

When a dependency violation is detected:

1. Block the downstream skill from loading.
2. Record the violation in the memory packet as a `BLOCKED` phase status.
3. Surface the blocking dependency to the user with the name of the missing upstream output.
4. Propose a resolution: either complete the upstream skill first, or provide the missing artifact directly.

---

## Graph Version

Version: 1.0.0
Covers: all 13 domain skills defined in `skills/`
Last updated: 2026-05-06