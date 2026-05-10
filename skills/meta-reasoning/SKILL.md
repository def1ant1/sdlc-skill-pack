---
name: meta-reasoning
description: Evaluates the quality, coherence, and reliability of AI reasoning chains, detects cognitive biases and logical fallacies, and recommends corrective interventions before outputs are acted upon.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, alignment-engine, telemetry]

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

Reasoning quality assurance layer for the cognitive runtime. Intercepts reasoning chains
before they drive actions, evaluates them for logical validity, bias patterns, and confidence
calibration, and recommends whether to proceed, revise, or escalate.

## Activation Triggers

- Cognitive-runtime completes a reasoning step and requests quality gate approval
- Alignment-engine flags a potential reasoning anomaly for deeper analysis
- Operator configures a workflow to require mandatory meta-reasoning review
- Confidence score on a reasoning output falls below the configured threshold

## Execution Protocol

1. **Load reasoning chain**: Retrieve the full chain of thought — premises, inference steps,
   intermediate conclusions, and final output — from the cognitive-runtime context.

2. **Check logical validity**: Verify that each inference step follows from its premises;
   flag invalid deductions, unsupported jumps, and circular reasoning.

3. **Detect cognitive biases**: Screen for known bias patterns — confirmation bias,
   anchoring, availability heuristic, sunk-cost reasoning, and scope insensitivity.

4. **Assess confidence calibration**: Compare stated confidence levels with historical
   accuracy for the same reasoning type; flag overconfident or underconfident assertions.

5. **Score reasoning quality**: Compute an aggregate quality score (0–100) across logical
   validity, bias-freedom, evidence grounding, and calibration dimensions.

6. **Recommend intervention**: If score exceeds threshold, approve chain for action. If below,
   recommend one of: REVISE (regenerate with bias correction prompts), EXPAND (gather more
   evidence), or ESCALATE (human review via hitl-dashboard).

## Output Format

Meta-reasoning report with: `reasoning_chain_id`, `quality_score`, `bias_flags` (list),
`logical_errors` (list), `calibration_delta`, `recommendation` (APPROVE/REVISE/EXPAND/ESCALATE),
and intervention guidance.

## References

- `references/bias-catalog.md` — 20 cognitive bias patterns, detection heuristics, correction prompts