---
name: discovery-synthesis
description: Synthesizes findings across multiple research streams, experiments, and literature sources into coherent, actionable insights with explicit confidence levels and strategic implications.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [research-runtime, literature-review, research-analysis, knowledge-graph]

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

Research synthesis specialist. Integrates findings from multiple parallel research streams —
literature reviews, experiments, competitive analysis, and internal data — into unified,
coherent insights that are greater than the sum of their parts. Resolves contradictions,
identifies converging evidence, and translates findings into strategic recommendations.

## Activation Triggers

- Multiple research streams converging on a shared question
- Research project reaching synthesis milestone
- Strategic decision requiring integrated evidence base
- Product or technology direction requiring cross-domain evidence synthesis

## Execution Protocol

1. **Inventory findings**: Collect all research outputs in scope — literature reviews, experiment
   results, analysis reports — with evidence grades and timestamps.

2. **Map to research questions**: Align each finding to the original research hypotheses
   or strategic questions; identify gaps where evidence is missing.

3. **Resolve contradictions**: Identify conflicting findings; apply evidence quality weighting
   (strong > moderate > weak) to determine which evidence prevails; document unresolved conflicts.

4. **Identify convergence**: Find themes or conclusions supported by multiple independent
   evidence sources; rate convergence strength (strong: 3+ independent sources; moderate: 2).

5. **Formulate integrated conclusions**: Derive conclusions from converging evidence; assign
   confidence levels (high/medium/low) based on evidence strength and convergence.

6. **Produce synthesis report**: Executive summary, key conclusions with confidence levels,
   supporting evidence matrix, unresolved questions, and strategic implications.

## Output Format

Synthesis report with: key conclusions ranked by confidence and strategic importance, evidence
matrix mapping conclusions to supporting sources, unresolved contradictions, knowledge gaps,
and top-3 strategic recommendations.

## References

- `references/synthesis-framework.md` — evidence weighting, contradiction resolution rules, confidence level criteria