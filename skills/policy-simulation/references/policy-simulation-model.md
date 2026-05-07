# Policy Simulation Model Reference

## Policy Impact Assessment Framework

### Simulation Scope Dimensions

| Dimension | Options | Assessment Impact |
|---|---|---|
| Population scope | All users / Segment / Geographic / Role-based | Compliance burden, equity impact |
| Temporal scope | Immediate / Phased (30/60/90 days) / Conditional | Change management, rollout risk |
| Enforcement mode | Hard block / Soft block (warn+log) / Audit only | Friction vs. visibility tradeoff |
| Reversibility | Permanent / Time-limited / Conditional | Risk of over-correction |

---

## Behavioral Change Model

Predict adoption rates and compliance behavior after policy enforcement:

```
BEHAVIORAL CHANGE MODEL:
  adoption_rate(t) = target_rate × (1 - exp(-k × t))

  where:
    t = days since policy enforcement
    k = adoption_speed_constant (calibrated from historical policy rollouts)
    target_rate = long-run compliance rate (typically 0.85-0.98 for mandatory policies)

  adoption_speed_constant calibration:
    k = 0.05: Slow adoption (complex behavior change, high friction)
    k = 0.10: Moderate adoption (clear instructions, tooling provided)
    k = 0.20: Fast adoption (automated enforcement, minimal user action required)

  Exception rate: target_rate = 1.0 - exception_rate
    exception_rate = (exempt_users / total_affected_users) × exception_grant_rate
```

---

## Impact Categories

### Category 1: Operational Impact

```yaml
operational_impact:
  friction_score:
    # Weighted average of friction across affected workflows
    calculation: "Σ (workflow_weight × workflow_friction_score)"
    workflow_friction_score:
      adds_no_steps: 0.0
      adds_one_click: 0.2
      adds_form_submission: 0.5
      adds_approval_workflow: 0.8
      blocks_task_entirely: 1.0

  throughput_impact:
    # Estimated reduction in task throughput due to added friction
    formula: "friction_score × tasks_per_day × average_friction_delay_minutes"

  error_rate_impact:
    # Whether policy enforcement may increase errors (e.g., workarounds)
    direction: "increase" | "neutral" | "decrease"
    magnitude: float  # % change in error rate
```

### Category 2: Compliance Impact

```yaml
compliance_impact:
  regulation_addressed: ["GDPR Art. 32", "HIPAA §164.312"]
  compliance_gap_before: 0.23  # Fraction of activity out of compliance
  compliance_gap_after: 0.02   # Residual non-compliance after enforcement

  residual_risk_sources:
    - "Exempt users (3% of population)"
    - "Edge cases not covered by policy scope"
    - "Technical enforcement lag (policy takes effect in 48h)"
```

### Category 3: Equity Impact

```yaml
equity_impact:
  disparate_impact_check:
    # Check whether policy disproportionately burdens specific groups
    FOR each protected_group g:
      burden_ratio = friction_score[g] / friction_score[overall_population]
      IF burden_ratio > 1.20:
        FLAG "Potential disparate impact on " + g
        RECOMMEND "Review policy scope for group-specific exceptions"
```

---

## Simulation Scenarios

For each policy proposal, simulate:

```yaml
scenarios:
  - id: "BASE"
    name: "Policy as proposed"
    enforcement_mode: "hard_block"
    rollout: "immediate"

  - id: "PHASED"
    name: "Phased rollout — 30-day soft block then hard block"
    enforcement_mode: "soft_block_then_hard"
    phase_1_days: 30
    phase_2_days: 60

  - id: "AUDIT_ONLY"
    name: "Audit-only — no enforcement, visibility only"
    enforcement_mode: "audit"
    rollout: "immediate"
    note: "Establishes compliance baseline before enforcement"

  - id: "SEGMENT"
    name: "Segment rollout — high-risk departments first"
    enforcement_mode: "hard_block"
    initial_scope: "departments=[finance, legal]"
    full_scope_date: "T+30"
```

---

## Unintended Consequence Detection

```
FUNCTION detect_unintended_consequences(policy, simulation_results):
    risks = []

    # Risk 1: Shadow IT — users route around policy to less-monitored systems
    IF simulation_results.blocked_activity_pct > 0.20:
        risks.append({
            type: "shadow_it",
            probability: HIGH if policy.has_alternatives else MEDIUM,
            mitigation: "Provide sanctioned alternative; monitor alternative channels"
        })

    # Risk 2: Productivity cliff — critical workflows blocked at peak times
    IF simulation_results.critical_workflow_block_rate > 0.05:
        risks.append({
            type: "productivity_cliff",
            probability: HIGH,
            mitigation: "Add time-limited emergency bypass with logging"
        })

    # Risk 3: Exception abuse — policy with exceptions creates loophole
    IF policy.has_exceptions AND simulation_results.exception_request_rate > 0.30:
        risks.append({
            type: "exception_abuse",
            probability: MEDIUM,
            mitigation: "Tighten exception criteria; require manager approval"
        })

    RETURN risks
```

---

## Policy Simulation Report Format

```yaml
policy_simulation_report:
  report_id: "PSR-20260507-001"
  policy_id: "POL-DATA-RESIDENCY-003"
  policy_name: "EU Data Residency Enforcement"
  simulation_date: "2026-05-07"

  affected_users: 1240
  affected_workflows: 34
  affected_systems: 8

  scenarios_simulated: [BASE, PHASED, AUDIT_ONLY]

  recommended_scenario: "PHASED"
  recommendation_rationale: |
    Phased rollout reduces operational disruption (friction score 0.34 vs. 0.61 for
    immediate enforcement) while achieving the same long-run compliance rate (97.2%).
    The 30-day soft block period gives teams time to adapt workflows.

  impact_summary:
    operational_friction_score: 0.34  # PHASED scenario
    throughput_impact_pct: -8.2       # 8.2% estimated productivity reduction
    compliance_gap_after: 0.028
    equity_issues_flagged: 0
    unintended_consequences: 1        # Exception abuse risk (MEDIUM)

  go_no_go_recommendation: "GO_WITH_CONDITIONS"
  conditions:
    - "Tighten exception criteria before enforcement"
    - "Provide migration tooling for affected teams by T-14"
    - "Monitor shadow IT channels for first 60 days post-enforcement"
```