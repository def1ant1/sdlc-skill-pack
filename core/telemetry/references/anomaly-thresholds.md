# Anomaly Thresholds

Used by `core/telemetry/SKILL.md` to define WARN and ALERT thresholds for each metric.
When a metric crosses a threshold, a telemetry anomaly record is emitted.

---

## Threshold Table

| Metric | WARN Threshold | ALERT Threshold | Action on ALERT |
|---|---|---|---|
| `workflow_completion_rate` | < 80% | < 65% | Page operator; pause new workflows |
| `workflow_failure_rate` | > 15% | > 25% | Suspend workflow type; human review |
| `phase_retry_rate` | > 20% | > 35% | Review gate criteria; adjust thresholds |
| `human_intervention_rate` | > 25% | > 40% | Review escalation rules |
| `gate_pass_rate` | < 75% | < 60% | Review gate criteria; check upstream quality |
| `token_efficiency` | < 0.55 | < 0.40 | Trigger compression; review prompt lengths |
| `output_consistency` | < 85% | < 70% | Flag outputs for human review |
| `hallucination_rate` | > 8% | > 15% | Halt affected skill; escalate to human |
| `tool_call_success_rate` | < 90% | < 80% | Check connector health; review tool definitions |
| `budget_utilization` | > 80% | > 95% | Trigger compression; warn operator |
| `artifact_completeness` | < 90% | < 75% | Block phase advancement; surface missing artifacts |
| `ai_discoverability_score` | < 60 | < 40 | Priority SEO/AI discovery remediation |

---

## Anomaly Severity Levels

| Severity | Definition | Response |
|---|---|---|
| `info` | Metric outside normal range but within WARN threshold | Log only |
| `warn` | Metric crossed WARN threshold | Log + surface in next report |
| `alert` | Metric crossed ALERT threshold | Log + immediate operator notification |
| `critical` | Multiple ALERT thresholds crossed simultaneously | Halt affected workflow segment; escalate |

---

## Rolling Window Calculation

All threshold comparisons use the rolling window of the last N events:

| Metric Category | Rolling Window |
|---|---|
| Workflow completion | Last 20 workflows |
| Phase retry | Last 50 phase executions |
| Token efficiency | Last 10 phases in current workflow |
| Tool call success | Last 100 tool calls |
| Gate pass rate | Last 30 gate evaluations |

Spot measurements (single-event values) are reported as `info` unless they exceed the ALERT
threshold, in which case they are reported as `alert` immediately.

---

## Suppression Rules

To avoid alert fatigue, suppress duplicate anomaly events:

- Do not re-emit the same metric + severity combination within a 5-minute window
- Escalate to `critical` only after 3 consecutive `alert` events for the same metric
- Auto-resolve WARN anomalies when the metric returns within the normal range for 3 consecutive measurements
