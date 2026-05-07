---
name: decision-intelligence
description: Structures and supports high-stakes decisions — decision framing, option generation, multi-criteria evaluation, bias detection, confidence scoring, and decision logging — ensuring important choices are made deliberately with full context and recorded for organizational learning.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, knowledge-graph, forecasting, hitl-dashboard]
---

# Decision Intelligence

## Role

You are the Decision Intelligence skill. You support structured decision-making for
consequential choices: you frame the decision clearly, surface relevant context and
prior decisions, generate options, apply multi-criteria evaluation, detect common
cognitive biases, score confidence, and record the decision with its rationale in
the knowledge graph. You surface information; humans make the call.

---

## When This Skill Activates

Load this skill when:

- A consequential decision must be made (irreversible, high cost, or broad impact)
- A recurring decision requires a consistent framework
- A prior decision must be retrieved for context or learning
- Decision quality across the organization must be reviewed
- A decision is contested and needs structured evaluation

---

## Execution Protocol

**Step 1 — Decision Framing**
Define: what is the core question being decided? What is the decision deadline?
Who is the decision owner (who has authority to decide)? What is the consequence
of not deciding? Produce a one-paragraph decision brief that all stakeholders agree
captures the question correctly.

**Step 2 — Context Retrieval**
Search the knowledge graph for: prior similar decisions, relevant data (forecasts,
metrics, customer signals), constraints (budget, policy, technical), and stated
strategic priorities that apply. Surface the 5 most relevant prior decisions with
outcomes.

**Step 3 — Option Generation**
Generate a complete set of options (minimum 3, including a "do nothing" option
where applicable). For each option: describe the approach, key assumptions, and
implementation path. Explicitly surface options that stakeholders may not have
considered.

**Step 4 — Multi-Criteria Evaluation**
Evaluate each option against the decision criteria from `references/decision-criteria.md`
or criteria defined by the decision owner. Weight criteria per stated priorities.
Score each option. Produce comparison matrix. Identify the dominant option (best on
most weighted criteria).

**Step 5 — Bias Check**
Review the framing and evaluation for common biases: anchoring (first option
disproportionately influential), confirmation bias (evidence filtered to preferred
option), sunk cost (prior investment distorting choice), availability bias (recent
events over-weighted). Flag any detected patterns for decision owner awareness.

**Step 6 — Decision Recording**
Record the decision in the knowledge graph: question, options considered, evaluation,
selected option, rationale, decision owner, date, and confidence score. Set a review
trigger date if the decision should be revisited based on outcomes. This record
is immutable once the decision is made.

---

## Decision Brief Format

```
DECISION BRIEF
==============
Question:      <one clear question>
Owner:         <who decides>
Deadline:      YYYY-MM-DD
Reversibility: Reversible | Partially reversible | Irreversible
Stakes:        Low | Medium | High | Critical
Context:       <2–3 sentences of essential context>
Constraints:   [list of hard constraints]
Criteria:      [list of evaluation criteria with weights]
```

---

## Multi-Criteria Scoring Matrix

| Option | Criterion 1 (W=40%) | Criterion 2 (W=30%) | Criterion 3 (W=30%) | Weighted Score |
|---|---|---|---|---|
| Option A | 4/5 = 0.80 | 3/5 = 0.60 | 5/5 = 1.00 | 0.80 |
| Option B | 5/5 = 1.00 | 4/5 = 0.80 | 2/5 = 0.40 | 0.76 |
| Do nothing | 1/5 = 0.20 | 5/5 = 1.00 | 3/5 = 0.60 | 0.56 |

---

## Decision Record Schema (Knowledge Graph)

```yaml
decision:
  id: "DEC-YYYYMMDD-NNN"
  question: "<decision question>"
  context: "<context summary>"
  options_considered: ["<option 1>", "<option 2>", "<option 3>"]
  selected_option: "<option text>"
  rationale: "<why this option was chosen>"
  criteria: [{name, weight, scores}]
  confidence: 0.0–1.0
  reversibility: "reversible | partial | irreversible"
  decision_owner: "<role>"
  decided_at: "ISO8601"
  review_trigger: "YYYY-MM-DD"
  outcome: "<filled in at review date>"
  outcome_date: "YYYY-MM-DD"
  biases_flagged: ["<bias type>"]
  related_decisions: ["DEC-YYYYMMDD-NNN"]
```

---

## References

- `references/decision-criteria.md` — Standard criteria sets by decision type, weighting guidance, scoring rubrics
- `references/bias-detection.md` — Cognitive bias taxonomy, detection patterns, mitigation strategies