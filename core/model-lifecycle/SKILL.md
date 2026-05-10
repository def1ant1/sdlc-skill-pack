---
name: model-lifecycle
description: Orchestrates the full lifecycle of enterprise AI models from fine-tuning through promotion, production serving, continuous monitoring, and retirement with governed approval gates at each transition.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [lora-lifecycle, model-evaluation, benchmark-factory, governance, telemetry]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Model lifecycle governance manager. Coordinates model training runs, evaluation against
benchmark gates, promotion to production serving, continuous quality monitoring, and graceful
retirement — all within operator-defined approval boundaries and with full audit trail.

## Activation Triggers

- Fine-tuning or distillation run completed and ready for evaluation
- Benchmark gate evaluation required for promotion decision
- Model promotion proposed requiring governance review
- Production model quality degradation detected
- Model retirement scheduled or triggered by supersession

## Execution Protocol

1. **Register model candidate**: Record model-id, base model, training configuration, dataset
   lineage, training objective, and artifact storage path in the model registry.

2. **Run benchmark evaluation**: Invoke benchmark-factory to evaluate against all mandatory
   quality gates for the model tier; collect per-benchmark scores.

3. **Review gate results**: Check all thresholds — any gate failure blocks promotion; output
   detailed failure analysis for remediation.

4. **Route promotion request**: Score ≥ all thresholds: auto-promote if Level-0 policy;
   else submit to governance queue for operator approval.

5. **Deploy to production**: Coordinate with local-runtime for serving configuration; execute
   canary deployment (5% traffic for 30 minutes); validate quality metrics on canary.

6. **Monitor in production**: Track quality scores, error rates, and latency continuously;
   auto-rollback if quality drops below the degradation threshold.

7. **Execute retirement**: Graceful traffic drain; archive model artifacts to cold storage;
   update registry status; notify dependent routing policies.

## Output Format

Lifecycle action report: evaluation scorecard, gate pass/fail status, promotion approval or
block with rationale, deployment status, and production quality baseline metrics.

## References

- `references/model-promotion-gates.md` — benchmark thresholds per model tier, canary validation criteria, rollback triggers