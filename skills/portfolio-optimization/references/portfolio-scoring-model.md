# Portfolio Scoring Model Reference

## Scoring Criterion Definitions

### Criterion 1: Strategic Alignment (30%)

Measures how directly the initiative supports the organization's declared strategic objectives.

| Score | Description |
|---|---|
| 9–10 | Directly enables a top-3 strategic priority; explicitly named in strategy document |
| 7–8 | Strongly supports a strategic priority, though not explicitly named |
| 5–6 | Relevant to strategy but indirect; multiple hops to strategic objective |
| 3–4 | Adjacent to strategy; defensible link but not obvious |
| 1–2 | Minimal strategic relevance; primarily operational or technical debt |

### Criterion 2: Expected ROI (25%)

Quantified expected return relative to the investment required.

```
roi_score = min(10, (expected_benefit_usd / investment_usd - 1) × 2)
```

| ROI Multiple | Score |
|---|---|
| > 5× | 10 |
| 3–5× | 8–9 |
| 2–3× | 6–7 |
| 1.5–2× | 4–5 |
| 1–1.5× | 2–3 |
| < 1× | 0–1 |

For non-financial benefits (regulatory compliance, risk reduction), use avoided cost as
the benefit numerator.

### Criterion 3: Risk-Adjusted NPV (20%)

Net present value discounted for execution risk:

```
risk_adjusted_npv = npv × (1 - execution_risk_score / 10)
npv_score = min(10, risk_adjusted_npv / reference_npv_unit)
```

**Execution risk factors:** technical complexity, dependency on unproven technology,
team capability gap, external dependencies, regulatory uncertainty.

### Criterion 4: Capacity Fit (15%)

How well the initiative fits within current and projected capacity:

| Fit | Score |
|---|---|
| Fully funded; resources available and committed | 10 |
| Resources available; minor allocation required | 7–8 |
| Resources partially available; recruitment/reallocation needed | 4–6 |
| Significant capacity gap; requires headcount growth or major reallocation | 1–3 |

### Criterion 5: Time-to-Value (10%)

How quickly meaningful value is delivered:

| First Value Delivery | Score |
|---|---|
| < 30 days | 10 |
| 30–90 days | 8 |
| 90–180 days | 6 |
| 180–365 days | 4 |
| > 365 days | 2 |

---

## Constraint Types

### Hard Constraints (Must Satisfy)

| Constraint | Definition |
|---|---|
| Regulatory/mandatory | Initiative is required by law or regulation — must include |
| P0 commitment | Committed to external stakeholder — must include |
| Budget ceiling | Total portfolio investment ≤ approved budget |
| Headcount cap | Total FTE allocation ≤ available capacity |

### Soft Constraints (Score Penalty)

| Constraint | Penalty |
|---|---|
| Dependency conflict | Initiative A requires Initiative B; B not in portfolio → -15 score |
| Risk concentration | > 40% of budget in single domain → -10 score to marginal adds |
| Single-vendor lock-in | Initiative creates critical dependency on single vendor → -5 score |

---

## Optimization Algorithm

For portfolios with ≤ 20 initiatives: integer linear programming (exact solution).
For portfolios with > 20 initiatives: greedy knapsack with local search refinement.

**Objective function:**
```
maximize Σ (initiative_score_i × selected_i)
subject to:
    Σ (investment_i × selected_i) ≤ budget_ceiling
    Σ (fte_i × selected_i) ≤ headcount_cap
    mandatory_initiative_i = 1 for all mandatory initiatives
    selected_i ∈ {0, 1}
```

---

## Pareto Frontier Enumeration

For executive trade-off visibility, enumerate the Pareto frontier:

1. Solve at 80% of budget → record portfolio and total score
2. Solve at 90%, 100%, 110%, 120% of budget → record each portfolio and score
3. Present as a curve: budget → total portfolio score, highlighting the recommended point

---

## Sensitivity Analysis Protocol

Test portfolio robustness to budget changes:

| Scenario | Budget | Question Answered |
|---|---|---|
| Constrained | -20% | Which initiatives would we cut first? |
| Baseline | 100% | Recommended allocation |
| Expanded | +20% | What additional initiatives unlock? |

For each scenario, report: initiatives included/excluded, total portfolio score, and
the marginal initiative (the initiative added/removed at the boundary).

---

## Initiative Record Format (Input)

```yaml
initiative:
  id: "INIT-20260507-012"
  name: "AI-Powered Contract Review"
  description: "Automate NDA and vendor contract review using alignment-safe LLM"

  strategic_alignment_tags: ["AI-Safety", "Legal-Efficiency"]
  strategic_alignment_score: 8

  investment:
    one_time_usd: 150000
    annual_recurring_usd: 40000
    fte_required: 1.5
    duration_months: 6

  expected_benefit:
    annual_savings_usd: 200000
    first_value_date: "2026-08-01"
    benefit_type: "cost-avoidance"

  risk:
    execution_risk_score: 3  # 0=low, 10=high
    dependencies: ["INIT-20260507-008"]  # Requires AI safety stack

  constraints:
    mandatory: false
    regulatory_requirement: false
```