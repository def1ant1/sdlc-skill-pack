---
name: hypothesis-generation
description: Applies abductive reasoning to literature review findings, anomaly signals, and enterprise knowledge graphs to generate testable, falsifiable research hypotheses with experimental design recommendations.
metadata:
  version: "1.0.0"
  category: research
  owner: research
  maturity: alpha
  dependencies: [research-runtime, literature-review, semantic-layer, telemetry]

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

Abductive reasoning engine for the autonomous research runtime. Synthesizes evidence gaps,
observed anomalies, and cross-domain knowledge graph patterns to generate novel, testable
hypotheses — each with clear falsification criteria and an experimental design outline
sufficient for research-runtime execution planning.

## Activation Triggers

- Literature-review identifies a knowledge gap requiring hypothesis formation
- Research-runtime completes an experiment and requests follow-up hypothesis generation
- Discovery-synthesis identifies a cross-stream pattern requiring a unifying hypothesis
- Operator requests hypothesis generation for a specific research domain

## Execution Protocol

1. **Load evidence context**: Retrieve literature review findings, identified gaps, relevant
   knowledge graph subgraphs, and any anomaly signals from telemetry or domain data.

2. **Apply abductive reasoning**: For each knowledge gap or anomaly, generate the simplest
   explanation that accounts for all observed evidence; enumerate 3–5 competing hypotheses.

3. **Formalize hypotheses**: Express each hypothesis in IF-THEN form with explicit independent
   variable (IV), dependent variable (DV), and proposed causal mechanism; ensure falsifiability.

4. **Score novelty and feasibility**: Rate each hypothesis on: literature novelty (not already
   tested), feasibility (data available, experiment executable), expected information gain,
   and business relevance.

5. **Design experiment outline**: For the top-ranked hypothesis, produce a minimal experiment
   design — measurement approach, required data sources, sample requirements, and success
   criteria.

6. **Emit hypothesis set**: Return ranked hypotheses with experiment outlines to research-runtime
   for execution planning.

## Output Format

Hypothesis set with: `research_context_id`, N hypotheses each containing `hypothesis_statement`
(IF-THEN), `iv`, `dv`, `mechanism`, `novelty_score`, `feasibility_score`, `information_gain_estimate`,
and `experiment_outline` for the top-ranked hypothesis.

## References

- `references/hypothesis-framework.md` — abductive reasoning protocol, SMART hypothesis criteria, experiment design templates