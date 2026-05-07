# Governance Report Template Reference

## RAG Status Thresholds

### Schedule Variance (SV)

```
schedule_variance = (completed_milestones / planned_milestones_to_date) - 1
```

| SV Range | Status | Color |
|---|---|---|
| SV ≥ 0 | On track or ahead | GREEN |
| -0.10 ≤ SV < 0 | Minor delay; expected recovery within period | AMBER |
| SV < -0.10 | Significant delay; recovery plan required | RED |

### Budget Variance (BV)

```
budget_variance = (actual_spend / planned_spend_to_date) - 1
```

| BV Range | Status | Color |
|---|---|---|
| BV ≤ 0.05 | Within budget | GREEN |
| 0.05 < BV ≤ 0.15 | Minor overspend; explainable and managed | AMBER |
| BV > 0.15 | Significant overspend; escalation required | RED |

### Combined RAG Rule

An initiative's overall RAG is the WORSE of its schedule and budget RAG status.
A single RED on either dimension results in an overall RED status.

---

## Weekly Status Report Structure

```
# Portfolio Status Report — Week of [DATE]

## Portfolio RAG Summary

| Status | Initiative Count | % of Portfolio |
|--------|-----------------|----------------|
| GREEN  | N               | X%             |
| AMBER  | N               | X%             |
| RED    | N               | X%             |

Total initiatives tracked: N
Total committed budget: $X
Total actual spend to date: $X (X% of annual budget)

---

## RED Initiatives — Requiring Attention

### [Initiative Name] (RED — [Schedule/Budget/Both])
- **Variance:** SV = -X%, BV = +X%
- **Root cause:** [One sentence]
- **Recovery plan:** [One sentence or "No recovery plan — escalation required"]
- **Owner:** [Name]
- **Decision required:** [Yes/No — if Yes, describe decision needed]

---

## AMBER Initiatives — Monitor Closely

[Brief table: Initiative | Issue | Owner | Next Review]

---

## Milestone Heatmap

[Table of all initiatives × upcoming 8 weeks, with milestone markers and RAG indicators]

---

## Budget Waterfall

[Budget: Allocated → Committed → Spent → Forecast-to-Complete → Variance]

---

## Top 5 Risks

| Risk ID | Initiative | Description | Probability | Impact | Severity | Owner | Mitigation |
|---------|------------|-------------|-------------|--------|----------|-------|------------|
| R001 | [Name] | [Description] | High | High | Critical | [Owner] | [Action] |

---

## Decisions Required This Week

| Decision | Initiative | Requested By | Deadline | Options |
|----------|------------|--------------|----------|---------|
| [Description] | [Name] | [Owner] | [Date] | [Option A / Option B] |

---

## Escalations Raised This Week

[List of escalations, to whom, and expected resolution timeline]

---

## Decisions Made Last Week

[Brief record of decisions made, by whom, and outcome]
```

---

## Escalation Routing Matrix

| Severity | Condition | Escalation Target | Response Time |
|---|---|---|---|
| Minor | AMBER schedule; recovery plan exists | Project lead | Next weekly cycle |
| Significant | RED schedule OR RED budget; no recovery plan | Program manager | Within 48 hours |
| Critical | RED on both dimensions; or initiative at risk of cancellation | Executive sponsor | Within 24 hours |
| Program-wide | > 30% of portfolio in RED; budget forecast > 120% | Governance board | Within 48 hours |

---

## Variance Calculation Formulas

```
# Earned Value Management (EVM) approach

Planned Value (PV) = Budget × (planned_milestones_to_date / total_milestones)
Earned Value (EV) = Budget × (actual_milestones_completed / total_milestones)
Actual Cost (AC) = cumulative_spend_to_date

Schedule Variance (SV) = EV - PV
Cost Variance (CV) = EV - AC
Schedule Performance Index (SPI) = EV / PV
Cost Performance Index (CPI) = EV / AC

Estimate at Completion (EAC) = Budget / CPI
Variance at Completion (VAC) = Budget - EAC
```

---

## Governance Record Schema

```yaml
governance_record:
  report_id: "PGOV-20260507-W19"
  period: "2026-05-01 to 2026-05-07"
  generated_at: "2026-05-07T08:00:00Z"
  generated_by: "program-governance skill"

  portfolio_summary:
    total_initiatives: 12
    green_count: 7
    amber_count: 3
    red_count: 2
    total_budget_usd: 4500000
    total_spent_usd: 1823000
    budget_utilization_pct: 40.5

  escalations_raised: 2
  decisions_required: 1
  milestones_due_this_week: 5
  milestones_completed_on_time: 4
  milestone_adherence_pct: 80.0

  risk_register_updates: 3
  new_risks_identified: 1
  risks_closed: 1
```