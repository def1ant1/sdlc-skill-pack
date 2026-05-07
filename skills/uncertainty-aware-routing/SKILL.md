---
name: uncertainty-aware-routing
description: Estimates inference confidence and uncertainty for AI model outputs, escalating low-confidence requests to higher-capability model tiers to maintain quality SLOs without unnecessary over-provisioning.
metadata:
  version: "1.0.0"
  category: model-lifecycle
  owner: platform
  maturity: alpha
  dependencies: [model-routing, reasoning-depth-estimation, telemetry]
---

## Role

Confidence-based inference escalation manager for the model routing layer. Intercepts model
outputs with low confidence scores or high uncertainty estimates and routes them to higher-capability
tiers for re-inference, maintaining quality SLOs while avoiding blanket over-provisioning.

## Activation Triggers

- Model inference produces an output with confidence score below the configured tier threshold
- Reasoning-depth-estimation flags a task as harder than the initially selected model tier can handle
- Multiple consecutive low-confidence outputs from the same model trigger proactive tier escalation
- Operator configures a workflow step with mandatory uncertainty validation

## Execution Protocol

1. **Assess output confidence**: Evaluate the model's confidence on its output using available
   signals — output probability (logit entropy), stated uncertainty, self-consistency across
   multiple samples, or embedding distance from training distribution.

2. **Classify uncertainty type**: Distinguish aleatoric uncertainty (inherent ambiguity in the
   task — cannot be resolved by more compute) from epistemic uncertainty (model capability gap
   — can be resolved by a more capable model).

3. **Apply escalation threshold**: Compare confidence score to the per-tier threshold; if below
   threshold and uncertainty is epistemic, initiate escalation to the next capability tier.

4. **Execute escalation**: Re-route request to the next tier model; set escalation flag to
   prevent further escalation loops; record cost delta from escalation.

5. **Compare outputs**: If the higher-tier output confidence is above threshold, return it;
   if still low-confidence, flag as genuinely ambiguous and return with uncertainty annotation.

6. **Log escalation record**: Record escalation trigger, source and target tiers, confidence
   scores, and cost impact for routing optimization feedback.

## Output Format

Routing escalation record with: `request_id`, `initial_model_id`, `initial_confidence_score`,
`uncertainty_type` (aleatoric/epistemic), `escalated_to_model_id`, `final_confidence_score`,
`cost_delta`, and `escalation_outcome` (RESOLVED/AMBIGUOUS).

## References

- `references/uncertainty-thresholds.md` — confidence scoring methods, tier escalation thresholds, aleatoric vs. epistemic classification