# Self-Improvement Protocol

Used by `core/autonomous-os/SKILL.md` to define the weekly improvement cycle,
what the OS learns from, and how it evolves its own skills, models, and priorities
autonomously within operator-approved governance boundaries.

---

## Improvement Cycle Overview

The OS runs a structured self-improvement cycle every Friday 08:00 UTC:

```
Phase 1: Observe   — Collect performance data from the past 7 days
Phase 2: Diagnose  — Identify degradations, regressions, and gaps
Phase 3: Prescribe — Generate improvement actions ranked by impact
Phase 4: Execute   — Run autonomous improvements (within authority)
Phase 5: Verify    — Confirm improvements took effect
Phase 6: Report    — Surface summary to operator
```

---

## Phase 1: Observe

Collect from telemetry (last 7 days):

```yaml
observation_inputs:
  workflow_quality:
    - quality_gate_pass_rate_by_skill
    - mean_output_score_by_model
    - task_completion_rate

  model_performance:
    - benchmark_scores_all_active_models
    - drift_delta_vs_prior_week
    - hallucination_rate_by_task_type

  runtime_economics:
    - cost_per_workflow_by_type
    - local_vs_cloud_ratio
    - gpu_utilization_avg_peak

  business_metrics:
    - mrr_delta
    - nrr
    - churn_rate
    - d7_d30_retention
    - nps_score

  customer_health:
    - pct_healthy_accounts
    - tickets_per_customer
    - onboarding_completion_rate

  gtm_performance:
    - organic_traffic_delta
    - ai_citation_rate
    - content_published_vs_planned

  compliance_posture:
    - open_compliance_gaps
    - evidence_freshness_violations
    - security_findings_by_severity
```

---

## Phase 2: Diagnose

Apply diagnostic rules to the observation data:

### Degradation Signals

| Signal | Threshold | Diagnosis |
|---|---|---|
| Quality gate pass rate drops | > 5% decline | Skill or model regression |
| Model benchmark score drops | > 5% from baseline | Model drift; retrain trigger |
| Hallucination rate rises | > 2% | Adapter quality degradation |
| Cost per workflow rises | > 20% week-over-week | Routing inefficiency |
| Cloud ratio rises | > local-first target | Local capacity issue |
| Churn rate rises | > 0.5pp month-over-month | Product or CS issue |
| D7 retention drops | > 3pp | Onboarding or activation problem |
| Compliance gap opened | Any new Critical gap | Immediate remediation required |
| AI citation rate drops | > 10% month-over-month | AI discoverability regression |

### Root Cause Classification

For each diagnosed issue, classify root cause:

| Root Cause | Indicator | Autonomous Action | Needs Approval |
|---|---|---|---|
| Model drift | Benchmark score decline | Trigger lora-lifecycle retrain | No |
| Routing inefficiency | High cloud cost | Update routing-economics rules | No |
| Skill regression | Gate fail rate rise | Flag for human review; run repo-intelligence | No (flag only) |
| Onboarding failure | TTFV > 5 days | Update onboarding track; A/B test | No |
| Content gap | AI citation drop | Trigger content-marketing brief | No |
| Compliance gap | New control gap | Evidence collection; escalate if Critical | Level-2 if Critical |
| Customer at-risk | Health score drop | Trigger CS intervention | No |

---

## Phase 3: Prescribe

Generate improvement actions ranked by ICE score:

```
ICE = Impact × Confidence × Ease (each 1–10)
```

Output a ranked action list:

```yaml
improvement_actions:
  - id: "IMP-YYYYMMDD-NNN"
    title: "<action title>"
    root_cause: "<diagnosis>"
    action_type: "model_retrain | routing_update | content_brief | skill_update | escalate"
    expected_impact: "<metric> improved by <amount>"
    ice_score: <number>
    autonomous: true | false
    approval_required: false | "Level-2 | Level-3"
    owner: "<skill or agent>"
    priority: P0 | P1 | P2 | P3
```

---

## Phase 4: Execute

Execute all autonomous improvement actions (no approval required):

### Autonomous Actions

**Model/Adapter Improvements:**
- Trigger `lora-lifecycle` retrain for any task with hallucination rate > 2%
- Trigger `synthetic-data` to generate fresh training examples for degraded tasks
- Update `local-runtime` routing table if a model was promoted or deprecated

**Routing/Cost Improvements:**
- Update `routing-economics.md` routing rules if cost analysis shows better path
- Adjust cloud overflow threshold if GPU utilization trend warrants it

**Content/GTM Improvements:**
- Generate content briefs for topics where AI citation rate has dropped
- Update `llms.txt` if new capabilities were shipped but not yet documented
- Queue newsletter section on any significant product improvement from the past week

**Customer Success Improvements:**
- Trigger intervention workflows for any account downgraded to At-Risk or Critical
- Generate KB article drafts for any ticket category with ≥ 3 unresolved occurrences
- Update onboarding tracks if TTFV data shows a consistent drop-off point

**Compliance Improvements:**
- Run evidence collection for any stale control (within operator-approved automation scope)
- Flag new compliance gaps for human review with remediation recommendation

### Actions Queued for Approval

Any action that requires Level-2 or Level-3 approval is formatted as an approval
request via `core/hitl-dashboard` with a full explainability record attached.

---

## Phase 5: Verify

One week after each improvement action, re-measure the target metric:

```yaml
verification:
  action_id: "IMP-YYYYMMDD-NNN"
  metric: "<what was targeted>"
  baseline: <value_before>
  target: <value_expected>
  actual: <value_measured>
  result: "improved | unchanged | degraded"
  next_action: "close | escalate | retry_with_different_approach"
```

If result = `degraded`: escalate to operator immediately with full context.
If result = `unchanged` after 2 cycles: escalate for human diagnosis.

---

## Phase 6: Report

Produce the weekly self-improvement report surfaced via `core/hitl-dashboard`:

```
APOTHEON SELF-IMPROVEMENT REPORT — Week of 2026-05-04
─────────────────────────────────────────────────────

OBSERVATIONS (7-day summary)
  Quality gate pass rate:  94.2% (▲ +1.1% vs prior week)
  Blended cost/workflow:   $0.043 (▼ -8.2% — routing optimization)
  Model drift alerts:      1 (qwen2.5-7b intent classifier)
  Business: MRR +6.8%, NRR 108%, Churn 1.9%

DIAGNOSES
  ▶ [MODEL DRIFT] qwen2.5-7b intent classifier: task_quality 0.77 → 0.71
  ▶ [CONTENT GAP] AI citation rate dropped 12% for "autonomous workflow" topic
  ▶ [CS ALERT] 3 accounts downgraded to At-Risk this week

AUTONOMOUS ACTIONS TAKEN
  ✓ Triggered lora-lifecycle retrain for intent-classifier adapter
  ✓ Generated 2 content briefs for AI workflow topic cluster
  ✓ Triggered CS interventions for 3 at-risk accounts

QUEUED FOR APPROVAL (2)
  [L2] Promote lora-lifecycle intent-classifier v4 (human sample review needed)
  [L2] Update compliance evidence for SOC2 CC6.1 (last collected 35 days ago)

VERIFICATION (prior week actions)
  ✓ Routing optimization → cost/workflow: $0.047 → $0.043 (improved)
  ✓ Onboarding track update → TTFV: 4.2d → 3.1d (improved)
  ○ Content brief for "local AI" topic → citations: pending (need 2 more weeks)

NEXT CYCLE: Friday 2026-05-15 08:00 UTC
```

---

## Governance Boundaries

The self-improvement protocol operates within these hard boundaries:

1. **Never modifies SKILL.md files autonomously** — skill behavior changes require operator review; the OS can flag improvements but not implement them
2. **Never promotes LoRA adapters without human sample review** — Level-2 approval always required for adapter promotion
3. **Never changes pricing, billing, or tenant configuration** — Level-3 always required
4. **Never suppresses its own telemetry or alters its own audit logs** — tampering is structurally blocked
5. **Never skips quality gates to accelerate the improvement cycle** — gates are invariant
6. **Self-improvement report is always produced**, even if no actions were taken — continuous visibility is non-negotiable
7. **Two-cycle rule**: if any autonomous action fails to improve the metric after 2 cycles, the action is escalated to a human; the OS does not retry indefinitely