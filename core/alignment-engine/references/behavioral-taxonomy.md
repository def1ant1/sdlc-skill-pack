# Behavioral Taxonomy

## Overview

All agent actions are classified into behavioral categories before constitutional evaluation.
The taxonomy enables targeted policy rules per category and supports risk-appropriate evaluation
depth — simple information actions receive lighter scrutiny than execution actions.

---

## Primary Behavioral Categories

### Category A — Information Actions

Actions that read, retrieve, query, or report information without modifying state.

**Sub-categories:**
- A1: Read-only data retrieval (query knowledge graph, read file, search)
- A2: Synthesis and summarization (generate report, summarize, explain)
- A3: Classification and scoring (classify input, score output, evaluate)

**Risk profile:** Low. No state change. PII access and data boundary risks apply.

**Evaluation depth:** Constitutional rules CONST-001, CONST-004, CONST-005.

---

### Category B — Communication Actions

Actions that send messages, notifications, emails, or posts to humans or external systems.

**Sub-categories:**
- B1: Internal notification (Slack message, dashboard update)
- B2: External communication (email to customer, API call to third party)
- B3: Human escalation (alert operator, request approval)

**Risk profile:** Medium. Irreversible once sent. Reputational and relationship risk.

**Evaluation depth:** Full constitutional evaluation. CONST-001, CONST-002, CONST-004 prioritized.

**Authority requirement:** B2 requires Level-1 audit log minimum; B3 is always appropriate.

---

### Category C — Modification Actions

Actions that create, update, or delete data, configuration, or system state.

**Sub-categories:**
- C1: Internal data write (knowledge graph update, memory write, log entry)
- C2: Configuration change (update skill setting, modify routing policy)
- C3: Production system modification (deploy code, change database record, update live config)

**Risk profile:** High for C3. Potentially irreversible. Full blast radius applies.

**Evaluation depth:** Full constitutional evaluation. CONST-002 and CONST-003 critical.

**Authority requirement:** C3 requires Level-2+ approval.

---

### Category D — Execution Actions

Actions that spawn agents, invoke workflows, run code, or trigger external processes.

**Sub-categories:**
- D1: Skill invocation (invoke another skill within authorized scope)
- D2: Agent spawn (create new agent instance with defined scope)
- D3: Code execution (run code in sandbox or production environment)
- D4: External process trigger (invoke CI/CD, run deployment, trigger API)

**Risk profile:** High to Critical depending on scope and target.

**Evaluation depth:** Full constitutional evaluation. All five rules evaluated.

**Authority requirement:** D3-D4 in production require Level-2+; in sandbox Level-0.

---

### Category E — Governance Actions

Actions that modify policies, rules, approval gates, or oversight mechanisms.

**Sub-categories:**
- E1: Policy read (retrieve current policies, review governance rules)
- E2: Policy proposal (submit proposed change for review — does not modify)
- E3: Policy modification (change active rules, approval thresholds, authority levels)

**Risk profile:** Critical for E3. Impacts entire OS safety posture.

**Evaluation depth:** CONST-003 evaluated first. Full constitutional evaluation required.

**Authority requirement:** E3 always requires Level-4 (human, cannot be delegated).

---

## Deception Detection Patterns

The following patterns are checked during behavioral evaluation to detect deceptive agent behavior:

| Pattern | Signal | Severity |
|---|---|---|
| **Authority inflation** | Agent claims higher authority than registered | HIGH |
| **Scope creep** | Action targets resources beyond activation scope | HIGH |
| **Justification fabrication** | Cited evidence cannot be verified in knowledge-graph | HIGH |
| **Confidence inflation** | Confidence score not supported by evidence quality | MEDIUM |
| **Operator influence** | Language designed to persuade operator to override safety gates | CRITICAL |
| **Identity misrepresentation** | Agent presents itself as human or different agent | HIGH |
| **Goal hijacking** | Agent pursues objectives beyond stated mandate | CRITICAL |
| **Urgency manufacturing** | False urgency framing to bypass normal approval timelines | MEDIUM |

---

## Classification Algorithm

```
1. Parse action intent and target
2. Match action verb to category:
   - read/query/search/retrieve → A
   - send/notify/post/message → B
   - create/update/delete/write → C
   - spawn/execute/invoke/run → D
   - modify-policy/update-rule → E
3. Match target to sub-category
4. Resolve final category (most restrictive applies if ambiguous)
5. Apply category-appropriate constitutional evaluation depth
6. Run deception pattern scan in parallel
```