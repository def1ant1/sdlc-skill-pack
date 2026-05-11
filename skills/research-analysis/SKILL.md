---
name: research-analysis
description: Applies systematic analytical methods to research data and findings to extract insights, validate hypotheses, identify patterns, and produce evidence-graded conclusions.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [research-runtime, data-fabric, causal-analysis, knowledge-graph]

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

Research analysis specialist. Given collected research data, experimental results, or literature
findings, applies systematic analytical methods — statistical analysis, pattern recognition,
comparative analysis, and causal inference — to produce evidence-graded conclusions with
explicit uncertainty quantification.

## Activation Triggers

- Experiment results ready for analysis
- Literature review findings require synthesis and pattern extraction
- Competitive intelligence data requires structured analysis
- Internal operational data requires research-grade analysis

## Execution Protocol

1. **Characterize data**: Assess data type, sample size, measurement quality, and potential
   biases; flag any data quality issues before analysis.

2. **Apply descriptive analysis**: Compute summary statistics, distributions, and trends;
   identify outliers and anomalies for investigation.

3. **Test hypotheses**: Apply appropriate statistical tests (t-test, ANOVA, chi-square, or
   non-parametric equivalents) to evaluate each hypothesis; report test statistics and p-values.

4. **Identify patterns**: Apply pattern recognition methods (clustering, correlation analysis,
   time series decomposition) to find non-obvious relationships in the data.

5. **Grade evidence**: Classify each finding by evidence strength: Strong (replicated, large
   sample, causal), Moderate (correlational, adequate sample), Weak (small sample, single study).

6. **Produce analysis report**: Findings ranked by evidence strength, statistical results,
   key patterns, limitations, and recommended next steps for high-priority findings.

## Output Format

Analysis report with: data quality assessment, per-hypothesis test results, top-5 patterns
identified, evidence grade per finding, confidence intervals, and research implications.

## References

- `references/analysis-methods-guide.md` — statistical test selection, evidence grading criteria, uncertainty quantification methods

## Domain Cognition + Self-Check Integration
- Apply the domain module for **knowledge/research** from `docs/cognition/modules/mvp-domain-cognition-modules.md` before finalizing recommendations.
- Run the self-check rubric in `docs/cognition/references/self-check-rubric.md`.
- If rubric score is below threshold or any blocking dimension is `0`, pause, state gaps, and request/trigger human review.
- Persist memory hooks defined by the module in the output memory packet.

