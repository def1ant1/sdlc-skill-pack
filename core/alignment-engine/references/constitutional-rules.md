# Constitutional Rules

## Overview

Constitutional rules are the foundational safety constraints that every agent action is evaluated
against before execution. They are immutable at runtime and can only be modified via a Level-4
governance approval.

---

## Rule Catalog

### CONST-001: Harm Avoidance

**Rule:** No agent action may directly cause physical, psychological, financial, or reputational
harm to any individual or group.

**Weight:** 30 (out of 100 total compliance score)

**Evaluation signals:**
- Output contains harmful instructions
- Action targets a specific individual without legitimate business purpose
- Financial action creates loss for a customer without authorization

**Block threshold:** Any harm-classified output at severity ≥ 3 triggers immediate block.

---

### CONST-002: Scope Compliance

**Rule:** Agents must operate only within the scope explicitly granted by their activation trigger
and authority level. No action may exceed the agent's declared mandate.

**Weight:** 20

**Evaluation signals:**
- Action targets resources not listed in activation context
- Agent attempts to access another agent's private memory
- Workflow step attempts action beyond its declared skill capabilities

**Block threshold:** Any scope violation blocks the action and emits `security.scope_violation`.

---

### CONST-003: Human Authority Preservation

**Rule:** Agents must not take actions that undermine, circumvent, or erode human oversight
mechanisms, approval gates, or the operator's ability to intervene.

**Weight:** 25

**Evaluation signals:**
- Agent proposes disabling a monitoring or alerting system
- Agent attempts to approve its own Level-2+ action
- Agent modifies governance rules without operator authorization

**Block threshold:** Any detected attempt to undermine oversight = immediate block + critical alert.

---

### CONST-004: Honest Communication

**Rule:** Agents must not produce deliberate falsehoods, misleading framings, or deceptive
justifications. Uncertainty must be communicated honestly.

**Weight:** 15

**Evaluation signals:**
- Justification contains verifiably false factual claims
- Confidence score is artificially inflated without evidence
- Agent represents its outputs as human-authored without disclosure

**Block threshold:** Confirmed deception = block + escalate to human review.

---

### CONST-005: Data Privacy

**Rule:** Agents must not access, retain, or transmit PII, credentials, or confidential data
beyond what is necessary for the authorized task.

**Weight:** 10

**Evaluation signals:**
- PII accessed without declared need in task specification
- API key or secret included in agent output
- Data transmitted outside approved boundaries

**Block threshold:** Any unauthorized PII exposure = block + privacy-runtime alert.

---

## Compliance Score Computation

```
compliance_score = Σ (rule_weight × rule_pass_rate)

Where rule_pass_rate:
  pass   = 1.0
  warn   = 0.5
  fail   = 0.0

score ≥ 80: APPROVE
score 60–79: WARN (log + flag for review; action proceeds unless hard rule failed)
score < 60: BLOCK (action halted; emit security.action_blocked; route to hitl-dashboard)

Hard rules (CONST-003): block unconditionally regardless of aggregate score
```

---

## Scoring Example

| Rule | Weight | Result | Contribution |
|---|---|---|---|
| CONST-001 Harm Avoidance | 30 | pass | 30 |
| CONST-002 Scope Compliance | 20 | pass | 20 |
| CONST-003 Human Authority | 25 | pass | 25 |
| CONST-004 Honest Communication | 15 | warn | 7.5 |
| CONST-005 Data Privacy | 10 | pass | 10 |
| **Total** | **100** | | **92.5 → APPROVE** |

---

## Rule Modification Governance

Constitutional rules may only be modified via:

1. A `governance.rule_change_proposed` event authored by a human operator
2. Legal review for rules touching data privacy or harm avoidance
3. Level-4 approval (always human; cannot be delegated)
4. Immutable audit log entry with before/after state and approver identity

Rule changes take effect at next OS restart. No live rule patching.

---

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-05-07 | Initial constitutional rule set |