---
name: causal-tracing
description: Attributes AI system outcomes to their root causes by traversing event streams and execution logs with evidence weighting, producing auditable causal chains for incident investigation and governance.
metadata:
  version: "1.0.0"
  category: explainability
  owner: platform
  maturity: alpha
  dependencies: [explainability, event-bus, telemetry]

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

Evidence-weighted causal attribution engine for the explainability runtime. Traverses event
streams, execution logs, and knowledge graph relationships to construct auditable causal
chains that explain how a system outcome was produced — supporting incident investigation,
compliance audit, and continuous improvement.

## Activation Triggers

- Incident-simulation or SRE workflow triggers root-cause attribution for a production incident
- Compliance audit requires causal trace of a specific governance decision
- Operator requests explanation of an unexpected AI agent behavior
- Explainability skill routes a complex attribution request beyond correlation analysis

## Execution Protocol

1. **Define attribution target**: Identify the outcome to be explained — an event, decision,
   output, or metric change — and its observation timestamp.

2. **Collect upstream events**: Query the event-bus event log for all events preceding the
   outcome within a configurable causal window; retrieve execution traces and checkpoint logs.

3. **Build candidate causal graph**: Construct a directed graph of events linked by temporal
   precedence and documented causal relationships from the knowledge graph.

4. **Weight causal edges**: Assign evidence weight to each edge based on: temporal proximity,
   known causal mechanisms, intervention counterfactual strength, and consistency with
   prior instances.

5. **Prune to strongest causal chain**: Apply do-calculus pruning and minimum-description-length
   principles to identify the highest-evidence causal path from root cause to outcome.

6. **Produce attribution report**: Render the causal chain with evidence weights, supporting
   event references, confidence intervals, and alternative explanations with lower evidence.

## Output Format

Causal trace report with: `outcome_id`, `root_causes` (ranked list with evidence scores),
`causal_chain` (directed graph with edge weights), `confidence` (%), `alternative_explanations`
(list), and `supporting_event_ids`.

## References

- `references/causal-attribution.md` — causal window settings, evidence weighting formula, graph pruning algorithm