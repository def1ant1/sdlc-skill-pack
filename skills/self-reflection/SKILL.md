---
name: self-reflection
description: Reviews AI-generated outputs against quality rubrics and stated objectives, identifies systematic improvement opportunities, and produces structured recommendations for capability enhancement.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, meta-reasoning, alignment-engine, telemetry]

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

Output quality reviewer and self-improvement advisor for the autonomous OS. Systematically
evaluates completed agent outputs against quality rubrics, identifies recurring failure
patterns, and generates actionable improvement recommendations for skills, prompts, and
agent configurations.

## Activation Triggers

- Agent completes a significant output (report, plan, code, analysis) requiring quality review
- Evolution-engine requests a quality assessment baseline before proposing improvements
- Operator requests a retrospective review of recent agent performance
- Alignment-engine detects quality degradation trend in an agent's outputs

## Execution Protocol

1. **Load output and context**: Retrieve the completed output, the original objective, any
   constraints, and the quality rubric applicable to the output type.

2. **Evaluate against rubric**: Score the output on each rubric dimension — completeness,
   accuracy, coherence, conciseness, actionability, and alignment with stated objective.

3. **Identify deficiencies**: Catalog specific gaps: missing required sections, unsupported
   claims, logical inconsistencies, misalignment with objective, or scope violations.

4. **Pattern-match against known failure modes**: Cross-reference deficiencies with the
   historical failure pattern library to identify recurring systemic issues vs. one-off errors.

5. **Generate improvement recommendations**: For each identified deficiency, produce a
   specific, actionable recommendation — prompt refinement, skill configuration change,
   additional context injection, or agent capability upgrade.

6. **Emit reflection record**: Publish the quality score, deficiency list, and ranked
   recommendations to the evolution-engine and requesting operator.

## Output Format

Reflection report with: `output_id`, `quality_score` (0–100), `rubric_scores` (per dimension),
`deficiencies` (list with severity), `recurring_patterns` (list), `recommendations` (ranked list
with implementation effort estimate).

## References

- `references/quality-rubric.md` — output type rubrics, scoring weights, failure pattern library