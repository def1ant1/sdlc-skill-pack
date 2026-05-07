# PRD Template

## Document Header

```
PRODUCT REQUIREMENTS DOCUMENT
==============================
Title:        <feature or initiative name>
PRD-ID:       PRD-YYYY-NNN
Author:       <owner>
Status:       Draft | In Review | Approved | Deprecated
Version:      x.y
Created:      YYYY-MM-DD
Last updated: YYYY-MM-DD
Approved by:  <stakeholder sign-offs>
```

---

## Section 1 — Problem Statement

**One-paragraph summary**: What problem exists? Who has it? What is the current experience
and why is it insufficient?

**Evidence**: Quantify the problem where possible — user research quotes, support ticket
volume, drop-off rates, revenue impact, competitive benchmarks.

**In scope / Out of scope**:
- In scope: [explicit list]
- Out of scope: [explicit list — equally important]

---

## Section 2 — Goals and Success Metrics

| Goal | Success Metric | Target | Baseline | Measurement Method |
|---|---|---|---|---|
| <primary goal> | <metric name> | <target value> | <current value> | <how measured> |
| <secondary goal> | <metric name> | <target value> | <current value> | <how measured> |

**Primary north star metric**: [single metric that defines success]

**Guardrail metrics** (must not degrade):
- [metric]: must remain ≥ [threshold]
- [metric]: must remain ≤ [threshold]

---

## Section 3 — User Stories

Format: `As a [persona], I want [capability] so that [outcome].`

### Must Have (P0)

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-001 | As a [persona], I want... | Given / When / Then |

### Should Have (P1)

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-002 | As a [persona], I want... | Given / When / Then |

### Nice to Have (P2)

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-003 | As a [persona], I want... | Given / When / Then |

---

## Section 4 — Functional Requirements

Number all requirements: `FR-NNN`. Each requirement must be testable.

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| FR-001 | The system shall... | P0 | — |

---

## Section 5 — Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Performance | P95 latency | ≤ 500ms |
| Availability | Uptime | ≥ 99.9% |
| Security | Auth required | All endpoints |
| Accessibility | WCAG level | AA |
| Scalability | Concurrent users | N |

---

## Section 6 — Dependencies

| Dependency | Type | Owner | Risk |
|---|---|---|---|
| [service/team] | API / data / decision | [owner] | [risk description] |

---

## Section 7 — Open Questions

| ID | Question | Owner | Due Date | Status |
|---|---|---|---|---|
| OQ-001 | [question] | [name] | YYYY-MM-DD | Open |

---

## Section 8 — Appendix

- Designs / mockups: [links]
- Research: [links]
- Related PRDs: [links]
- ADRs: [links]