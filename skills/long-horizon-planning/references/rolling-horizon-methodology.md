# Rolling Horizon Methodology Reference

## Rolling Horizon Framework

Rolling horizon planning maintains a planning window that advances with time:
- **Fixed horizon length:** The plan always covers a fixed duration (e.g., 12 months)
- **Rolling update:** At each review period, the horizon rolls forward and the plan is revised
- **Detail gradient:** Near-term periods planned in detail; far-term in outline

```
HORIZON STRUCTURE (12-month rolling, monthly review):

  Month 0 (now):
    [M1: DETAILED] [M2: DETAILED] [M3: DETAILED]   ← Tactical (weekly tasks)
    [M4-M6: MEDIUM]                                  ← Operational (monthly milestones)
    [M7-M12: OUTLINE]                                ← Strategic (quarterly goals)

  After Month 1 rolls:
    [M2: DETAILED] [M3: DETAILED] [M4: DETAILED]   ← M4 promoted to tactical
    [M5-M7: MEDIUM]
    [M8-M13: OUTLINE]                               ← New M13 added
```

---

## Planning Depth by Horizon Zone

| Zone | Horizon | Planning Depth | Update Frequency | Output Format |
|---|---|---|---|---|
| Tactical | 0–3 months | Day/week granularity | Weekly | Sprint tasks, Gantt chart |
| Operational | 3–6 months | Milestone granularity | Monthly | Milestone schedule |
| Strategic | 6–12 months | Quarterly goal granularity | Quarterly | OKR / goal tree |
| Vision | 12–36 months | Annual outcome level | Annually | Strategic narrative |

---

## Horizon Promotion Protocol

When the tactical zone boundary advances (e.g., Month 4 becomes Month 1):

```
PROMOTION STEPS:
  1. DETAIL EXPANSION: Convert operational plan for newly-tactical period
     - Decompose milestones into sprint tasks
     - Assign owners for each task
     - Identify dependencies and critical path
     - Allocate resources

  2. ASSUMPTION VALIDATION: Verify assumptions made when period was in operational/strategic zone
     - Check if key assumptions still hold
     - Update estimates based on latest data
     - Flag changed assumptions for stakeholder review

  3. RISK REASSESSMENT: Recalibrate risks as execution approaches
     - Risks that seemed distant may now be immediate
     - New risks may have emerged since last planning cycle

  4. COMMITMENT LOCK: Once in tactical zone, scope is locked unless:
     - Executive decision to change scope
     - Blocker makes current plan unexecutable
     - Documented change request process followed
```

---

## Rolling Forecast Update Rules

### Forecast Lock Zones

```yaml
forecast_lock_policy:
  locked_zone: "0–4 weeks from now"
  lock_rule: |
    Forecasts in this zone cannot be changed without executive approval.
    Purpose: Protect operational planning from constant re-planning churn.

  flexible_zone: "4–12 weeks from now"
  flex_rule: |
    Forecasts can be updated by team leads during monthly review.
    Changes require documentation of what changed and why.

  exploratory_zone: "12+ weeks from now"
  explore_rule: |
    Forecasts are provisional and expected to change.
    Updated based on new market data, strategic decisions, or learning.
```

### Forecast Update Triggers

```
MANDATORY UPDATE TRIGGERS (update plan immediately):
  - Key assumption invalidated (e.g., budget reduced > 20%)
  - Critical dependency blocked
  - Regulatory change affecting scope
  - Technology risk materially changes (e.g., dependency deprecated)

STANDARD UPDATE TRIGGERS (update at next review cycle):
  - Milestone slippage > 2 weeks in tactical zone
  - Resource availability change > 15%
  - Scope change request approved
  - Quarterly strategic review completed
```

---

## Scenario Planning Integration

Rolling horizon planning incorporates scenario planning for the strategic zone:

```yaml
strategic_zone_scenarios:
  base_scenario:
    probability: 0.60
    description: "Current trajectory; assumptions hold"
    planning_approach: "full_detail"

  upside_scenario:
    probability: 0.20
    description: "Market growth accelerates; budget increased"
    planning_approach: "capacity_surge_options"
    trigger_to_activate: "Q3 revenue > target × 1.20"

  downside_scenario:
    probability: 0.20
    description: "Budget constraint; prioritization required"
    planning_approach: "critical_path_only"
    trigger_to_activate: "Q3 revenue < target × 0.80"

  contingency_decisions:
    - trigger: "upside_scenario activated"
      decision: "accelerate_hiring + expand_scope_to_phase_2"
    - trigger: "downside_scenario activated"
      decision: "defer_phase_2 + reduce_headcount_by_2_FTE"
```

---

## Plan Representation Format

```yaml
rolling_horizon_plan:
  plan_id: "RHP-SDLC-2026"
  as_of: "2026-05-07"
  horizon_months: 12
  review_cycle: "monthly"

  tactical_zone:
    period: "2026-05 to 2026-07"
    items:
      - id: "TASK-001"
        name: "Complete skill reference files"
        owner: "platform-team"
        due_date: "2026-05-15"
        status: "IN_PROGRESS"
        completion_pct: 65
        dependencies: []

  operational_zone:
    period: "2026-08 to 2026-10"
    items:
      - id: "MILESTONE-001"
        name: "Phase 1 production deployment"
        owner: "engineering-lead"
        target_date: "2026-09-30"
        status: "ON_TRACK"
        key_dependencies: ["TASK-001", "TASK-002"]
        risk_level: "MEDIUM"

  strategic_zone:
    period: "2026-11 to 2027-04"
    items:
      - id: "GOAL-Q4-2026"
        name: "Enterprise customer onboarding (10 accounts)"
        owner: "go-to-market"
        target_quarter: "Q4-2026"
        confidence: 0.70
        key_assumptions:
          - "Sales team fully ramped by Q3"
          - "Product-market fit validated by pilot program"

  next_review_date: "2026-06-07"
  horizon_extension_date: "2026-06-07"  # Adds 2027-05 to plan
```