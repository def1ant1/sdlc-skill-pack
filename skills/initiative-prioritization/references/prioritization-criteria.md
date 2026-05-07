# Prioritization Criteria Reference

## Scoring Criterion Definitions

### Criterion 1: Strategic Alignment (30% weight)

**Definition:** How directly does this initiative advance a declared strategic objective?

| Score | Rubric |
|---|---|
| 5 | Initiative is explicitly named in the current strategic plan as a priority action |
| 4 | Initiative directly enables a top-3 strategic objective |
| 3 | Initiative supports a strategic objective, but indirectly or partially |
| 2 | Initiative is adjacent to strategy; defensible link but not obvious |
| 1 | Primarily operational or technical; minimal strategic connection |

---

### Criterion 2: Business Value (25% weight)

**Definition:** What quantified or qualitative business benefit does completion deliver?

| Score | Rubric |
|---|---|
| 5 | ROI > 3× or major risk eliminated (regulatory, operational) |
| 4 | ROI 2–3× or significant measurable improvement in key business metric |
| 3 | ROI 1.5–2× or moderate improvement in business metric |
| 2 | ROI 1–1.5× or qualitative improvement hard to quantify |
| 1 | Uncertain benefit; primarily maintenance or technical debt |

---

### Criterion 3: Urgency and Time-Sensitivity (20% weight)

**Definition:** How time-sensitive is this initiative? What is the cost of delay?

| Score | Rubric |
|---|---|
| 5 | Regulatory deadline in < 90 days; or committed to external stakeholder with penalty |
| 4 | Market window closes in < 6 months; or significant competitive risk |
| 3 | Time-sensitive opportunity with clear degradation if delayed > 6 months |
| 2 | Beneficial to start now but delay < 12 months has low cost |
| 1 | No significant time sensitivity; can wait indefinitely |

---

### Criterion 4: Risk (15% weight)

**Definition:** What is the initiative's execution risk? (Higher risk = lower score)

| Score | Rubric |
|---|---|
| 5 | Well-understood scope, proven technology, experienced team; low risk |
| 4 | Some uncertainty but manageable; team has relevant experience |
| 3 | Moderate complexity; some novel technology or team skill gap |
| 2 | High complexity or dependency; significant uncertainty |
| 1 | High risk: unproven technology, unclear scope, major dependencies |

---

### Criterion 5: Implementation Feasibility (10% weight)

**Definition:** Can we actually execute this initiative given current capacity and capabilities?

| Score | Rubric |
|---|---|
| 5 | All resources committed; initiative can start immediately |
| 4 | Resources available with minor allocation decisions needed |
| 3 | Resources partially available; manageable gap |
| 2 | Significant capacity gap; requires hiring or major reallocation |
| 1 | Capacity gap cannot be closed within the planning horizon |

---

## Weighted Composite Score Formula

```
priority_score = (strategic_alignment × 0.30) +
                 (business_value × 0.25) +
                 (urgency × 0.20) +
                 (risk × 0.15) +
                 (feasibility × 0.10)

# Normalize to 0-100 scale:
priority_score_normalized = (priority_score / 5) × 100
```

---

## Tiebreaker Rules

When two initiatives have composite scores within 2 points of each other:

1. **Urgency tiebreaker:** Higher urgency score wins
2. **Strategic alignment tiebreaker:** Higher strategic alignment wins
3. **Feasibility tiebreaker:** Higher feasibility (can start sooner) wins
4. **Human judgment:** If still tied after three tiebreakers, refer to program manager

---

## Conflict Resolution Process

Conflicting priorities arise when multiple stakeholders assert different rankings:

1. **Surface the conflict:** Document the disagreeing parties and their stated priorities
2. **Identify the basis:** Determine if disagreement is about scoring inputs (fact-based) or
   scoring weights (preference-based)
3. **Resolve fact-based conflicts:** Present evidence; most recent/authoritative data wins
4. **Escalate preference-based conflicts:** Route to the governance committee for decision
5. **Document the resolution:** Record the decision, who made it, and the rationale
6. **Flag to governance:** Any unresolved priority conflict is surfaced in the weekly
   governance report as "decision required"

---

## Sequencing Recommendations

Given a prioritized list, generate sequencing recommendations:

```
FOR each initiative in priority_score order (highest first):
    IF capacity available in planning window:
        ASSIGN recommended_start_window = earliest available slot
    ELIF dependency_on_initiative_X_not_yet_started:
        ASSIGN recommended_start_window = after initiative X completion
    ELSE:
        MARK as deferred
        RECORD deferral_reason = "capacity constraint" | "dependency block"
```

**Output:** Prioritized and sequenced initiative list with recommended start windows and
a separate deferred list with explicit deferral reasons.