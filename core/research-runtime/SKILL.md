---
name: research-runtime
description: Autonomous research coordination layer that formulates hypotheses, designs experiments, synthesizes findings from literature and internal data, and produces structured research artifacts.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [enterprise-search, knowledge-graph, retrieval-engine, synthetic-data]

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

Research orchestration core for autonomous enterprise R&D. Manages the full research lifecycle:
hypothesis formation, literature review, experiment design, data collection, analysis, and
synthesis into structured, evidence-graded research artifacts.

## Activation Triggers

- Research objective submitted by operator or strategic-planning
- Technology assessment requested for an architectural decision
- Competitive intelligence cycle triggered weekly
- Internal knowledge gap identified by skill-gap-engine

## Execution Protocol

1. **Frame research question**: Decompose the objective into specific hypotheses and evaluation
   criteria; define what evidence would confirm or refute each hypothesis.

2. **Search existing knowledge**: Query enterprise-search for internal documents and decisions;
   search external technical sources for relevant prior work and literature.

3. **Synthesize literature**: Extract key findings; identify consensus areas, contradictions,
   and gaps; score evidence quality per source.

4. **Design experiments or probes**: Plan data collection, model experiments, or simulation
   runs to test hypotheses not answered by existing literature.

5. **Execute and collect findings**: Run experiments; ingest results; apply research-analysis
   statistical methods; evaluate hypothesis support.

6. **Produce research artifact**: Structured report with abstract, methodology, findings with
   evidence grades, implications, and recommended next actions.

## Output Format

Research report with: framed hypotheses, methodology, per-hypothesis findings with evidence
grade, synthesis conclusions with confidence levels, and strategic implications.

## References

- `references/research-workflow.md` — lifecycle stages, evidence quality scoring, hypothesis validation criteria