# Constraint Catalog Reference

## Constraint Taxonomy

### Dimension 1: Constraint Type

| Type | Code | Definition | Example |
|---|---|---|---|
| Hard constraint | HC | Must be satisfied; violation = infeasible plan | "Budget cannot exceed $10M" |
| Soft constraint | SC | Should be satisfied; violation incurs penalty | "Prefer delivery before Q3" |
| Preference | PR | Nice to have; weighted in optimization | "Team prefers Python over Java" |
| Invariant | IV | Always true by definition; used for consistency checks | "Total allocated ≤ total available" |

### Dimension 2: Constraint Domain

| Domain | Code | Description |
|---|---|---|
| Resource | RES | Capacity limits on compute, budget, headcount, time |
| Dependency | DEP | Ordering constraints between tasks or components |
| Temporal | TMP | Deadline, duration, concurrency, scheduling constraints |
| Quality | QUA | Minimum performance, reliability, or correctness thresholds |
| Safety | SAF | Constraints protecting against harmful outcomes |
| Legal/Regulatory | LEG | Compliance obligations |
| Operational | OPS | Runtime behavior constraints (SLO, SLA, rate limits) |

---

## Constraint Definition Schema

```yaml
constraint:
  id: "CON-BUDGET-001"
  name: "Total Project Budget Cap"
  type: HC  # HC | SC | PR | IV
  domain: RES

  expression: "Σ(component_costs) ≤ budget_ceiling"
  parameters:
    budget_ceiling:
      value: 10000000
      currency: USD
      applies_to: "fiscal_year_2026"

  violation_handling:
    on_violation: REJECT_PLAN  # REJECT_PLAN | APPLY_PENALTY | WARN
    penalty_function: null  # For SC type: penalty = weight × violation_magnitude

  metadata:
    source: "finance_policy_2026"
    owner: "CFO"
    last_reviewed: "2026-01-15"
    review_cycle: "annual"
```

---

## Standard Constraint Library

### Resource Constraints

```yaml
# RC-001: Budget constraint
expression: "total_cost ≤ budget_ceiling"
type: HC
variables: [total_cost, budget_ceiling]

# RC-002: Headcount constraint
expression: "team_size ≤ max_headcount"
type: HC
variables: [team_size, max_headcount]

# RC-003: Compute capacity
expression: "peak_compute_demand ≤ provisioned_capacity × utilization_ceiling"
type: HC
variables: [peak_compute_demand, provisioned_capacity, utilization_ceiling]
default_utilization_ceiling: 0.80

# RC-004: Time budget
expression: "total_duration ≤ deadline - start_date"
type: HC
variables: [total_duration, deadline, start_date]
```

### Dependency Constraints

```yaml
# DC-001: Finish-to-start dependency
expression: "start(B) ≥ finish(A)"
type: HC
variables: [A, B]
description: "Task B cannot start until Task A is complete"

# DC-002: Minimum lag
expression: "start(B) ≥ finish(A) + lag"
type: HC
variables: [A, B, lag]

# DC-003: Resource conflict exclusion
expression: "NOT (active(A) AND active(B))"
type: HC
applies_when: "A and B share exclusive resource R"
```

### Quality Constraints

```yaml
# QC-001: Minimum test coverage
expression: "test_coverage ≥ coverage_floor"
type: HC
default_coverage_floor: 0.80

# QC-002: Maximum error rate
expression: "error_rate ≤ error_ceiling"
type: HC
default_error_ceiling: 0.001  # 0.1%

# QC-003: P95 latency SLO
expression: "p95_latency_ms ≤ latency_budget_ms"
type: HC
```

### Safety Constraints

```yaml
# SC-001: Alignment score floor
expression: "alignment_score ≥ 0.95"
type: HC
cannot_be_overridden: true

# SC-002: Human review gate
expression: "human_approved(action) = true BEFORE execute(action)"
type: HC
applies_to: "actions with severity ≥ HIGH"

# SC-003: Data residency
expression: "data_location IN allowed_jurisdictions"
type: HC
cannot_be_overridden: true
```

---

## Constraint Satisfaction Checking Protocol

```
FUNCTION check_constraints(plan, constraint_set):
    violations = []
    penalties = []

    FOR each constraint c IN constraint_set:
        IF c.type == HC:
            satisfied = evaluate(c.expression, plan)
            IF NOT satisfied:
                violations.append({
                    constraint_id: c.id,
                    severity: INFEASIBLE,
                    actual_value: evaluate_lhs(c.expression, plan),
                    allowed_value: evaluate_rhs(c.expression, plan)
                })

        ELIF c.type == SC:
            slack = evaluate_slack(c.expression, plan)
            IF slack < 0:
                penalty = c.penalty_weight × abs(slack)
                penalties.append({constraint_id: c.id, penalty: penalty})

    IF violations:
        RETURN ConstraintResult(feasible=False, violations=violations)
    ELSE:
        RETURN ConstraintResult(feasible=True, total_penalty=sum(penalties))
```

---

## Alternative Plan Generation

When hard constraints are violated, generate alternatives:

```
PROCEDURE generate_alternatives(violated_plan, violations):
    alternatives = []

    FOR each violation v IN violations:
        IF v.domain == RES:
            # Try reducing scope
            alt = reduce_scope(violated_plan, target=v.constraint)
            alternatives.append(alt)

            # Try extending timeline
            alt = extend_timeline(violated_plan, target=v.constraint)
            alternatives.append(alt)

        IF v.domain == DEP:
            # Try parallelizing where possible
            alt = parallelize_independent_tasks(violated_plan)
            alternatives.append(alt)

    RETURN rank_by_objective(alternatives)
```