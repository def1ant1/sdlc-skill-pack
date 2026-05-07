# Metric Catalog

Used by `core/telemetry/SKILL.md` to define all observable metrics, their collection
methods, baseline values, and reporting units.

---

## Workflow Metrics

| Metric | Description | Unit | Collection Method | Baseline Target |
|---|---|---|---|---|
| `workflow_completion_rate` | % of started workflows that reach terminal state | % | memory packet phase_status | > 85% |
| `workflow_failure_rate` | % of workflows ending in FAIL without recovery | % | memory packet phase_status | < 10% |
| `phase_retry_rate` | % of phases that required re-execution | % | quality_gate_status fail records | < 15% |
| `human_intervention_rate` | % of workflows requiring human approval or unblock | % | escalation events | < 20% |
| `time_in_phase_ms` | Wall-clock time from phase start to gate evaluation | ms | timestamps in memory packet | varies by phase |
| `gate_pass_rate` | % of gate evaluations that PASS on first attempt | % | quality_gate_status | > 80% |
| `gate_fail_rate` | % of gate evaluations that FAIL (first attempt) | % | quality_gate_status | < 15% |
| `remediation_cycles` | Number of gate re-evaluations per phase | count | quality_gate_status prior_fail_ref | < 2 per phase |

---

## LLM Quality Metrics

| Metric | Description | Unit | Collection Method | Baseline Target |
|---|---|---|---|---|
| `token_efficiency` | Ratio of useful output tokens to total tokens consumed | ratio | output tokens / total tokens | > 0.60 |
| `output_consistency` | % of output fields that match declared output schema | % | schema validation on skill output | > 90% |
| `hallucination_rate` | % of factual claims in output that contradict input context | % | consistency checker | < 5% |
| `tool_call_success_rate` | % of tool invocations returning valid, non-error results | % | tool call results log | > 95% |
| `reasoning_consistency` | % of decisions that reference a declared constraint or prior decision | % | decision audit | > 75% |
| `artifact_completeness` | % of declared output artifacts that are present and non-empty | % | artifact inventory check | > 95% |

---

## Token Economics Metrics

| Metric | Description | Unit | Baseline Target |
|---|---|---|---|
| `tokens_used` | Total tokens consumed in the phase | count | — |
| `budget_utilization` | tokens_used / allocated budget | % | < 90% per phase |
| `compression_triggered` | Whether compression ran during the phase | bool | Minimize |
| `budget_overage` | Tokens consumed beyond allocated budget | count | 0 |
| `rolling_efficiency` | Avg token_efficiency over last 10 phases | ratio | > 0.60 |

---

## GTM Metrics

| Metric | Description | Unit | Baseline Target |
|---|---|---|---|
| `campaign_roi` | Revenue attributed to campaign / campaign cost | ratio | > 3.0 |
| `conversion_rate` | Visitors who complete target action / total visitors | % | varies by channel |
| `seo_improvement_rate` | % change in organic search rank for target keywords | % | > 0 (improving) |
| `ai_discoverability_score` | Score from `validate_ai_discovery.py` (0–100) | score | > 70 |
| `content_publish_rate` | Content pieces published / planned per sprint | % | > 80% |

---

## Metric Collection Timing

| When | Metrics Collected |
|---|---|
| Phase start | time_in_phase_ms start, token snapshot |
| Phase completion | All workflow metrics, token delta, artifact check |
| Gate evaluation | gate_pass_rate, gate_fail_rate, remediation_cycles |
| Token threshold (50%) | Rolling efficiency check |
| Token threshold (75%) | Compression trigger, budget_utilization alert |
| Operator request | Full report across all categories |