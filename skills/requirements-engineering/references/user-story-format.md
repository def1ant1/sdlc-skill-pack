# User Story Format

## Core Format

```
As a [persona],
I want [capability or action],
So that [outcome or value].
```

**Personas must be defined** in the product ontology. Never use generic "user" — be
specific: "free-tier developer", "enterprise admin", "support agent".

---

## Acceptance Criteria (Gherkin)

Every story must have at least one scenario:

```gherkin
Scenario: <scenario name>
  Given <precondition — the state of the system>
  When  <action taken by the user or system>
  Then  <observable outcome>
  And   <additional assertion if needed>
```

### Multiple Scenarios Per Story

Cover: happy path, edge cases, error states, and boundary conditions.

```gherkin
Scenario: Happy path — <description>
  Given ...
  When ...
  Then ...

Scenario: Edge case — empty state
  Given ...
  When ...
  Then ...

Scenario: Error state — <description>
  Given ...
  When ...
  Then the system displays an error message: "<message text>"
  And  the user's data is not modified
```

---

## Story Sizing (T-shirt)

| Size | Story Points | Criteria |
|---|---|---|
| XS | 1 | Config change; no logic; < 2h |
| S | 2 | Single component; clear path; 2–4h |
| M | 3 | Moderate complexity; some unknowns; 0.5–1 day |
| L | 5 | Multiple components; cross-service; 1–3 days |
| XL | 8 | Significant complexity; requires spike; > 3 days |
| Epic | Split required | > 8 points — must be decomposed |

---

## Definition of Ready

A story is ready for sprint if ALL are true:

- [ ] Written in correct format (As a / I want / So that)
- [ ] Acceptance criteria complete (at least happy path + one error scenario)
- [ ] Sized ≤ L (XL requires decomposition)
- [ ] Dependencies identified and available
- [ ] Designs attached or explicitly not required
- [ ] No open blocking questions (OQ status = Resolved)

---

## Definition of Done

A story is done when ALL are true:

- [ ] All acceptance criteria pass (automated tests or verified manually)
- [ ] Code reviewed and merged
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] No new CRITICAL or HIGH vulnerabilities introduced
- [ ] Metrics instrumented (events tracked per event taxonomy)
- [ ] Feature flag enabled for release segment (if applicable)
- [ ] Documentation updated if user-facing

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| "As a user, I want to see a list" | No persona, no outcome | Specify persona; add "so that" |
| Technical story ("Refactor X class") | Not user-facing; no value statement | Write as enabler or use a task ticket |
| AC without observable outcome | Untestable | Rewrite with Then clause |
| Story > 8 points | Too large for a sprint | Decompose into sub-stories |
| Missing error scenarios | Incomplete coverage | Add at least one error AC |