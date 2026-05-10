---
name: literature-review
description: Conducts systematic literature searches, applies PRISMA-compliant screening and inclusion criteria, synthesizes findings into structured evidence summaries, and identifies knowledge gaps for hypothesis generation.
metadata:
  version: "1.0.0"
  category: research
  owner: research
  maturity: alpha
  dependencies: [research-runtime, enterprise-search, telemetry]

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

Systematic literature review engine for the autonomous research runtime. Executes
rigorous, reproducible literature searches across internal and external knowledge sources,
applies structured screening criteria, synthesizes evidence into graded summaries, and
surfaces knowledge gaps that can seed new research hypotheses.

## Activation Triggers

- Research-runtime initializes a new research project requiring literature baseline
- Hypothesis-generation skill requests evidence grounding for candidate hypotheses
- Operator submits a research question requiring systematic evidence synthesis
- Discovery-synthesis requests literature input for a cross-stream synthesis

## Execution Protocol

1. **Define search strategy**: Formalize the research question using PICO or SPIDER framework;
   construct Boolean search queries with inclusion/exclusion criteria and date range.

2. **Execute multi-source search**: Query enterprise knowledge graph, external academic
   databases (via configured connectors), and internal document repositories; record
   all search strings and result counts for reproducibility.

3. **Screen results**: Apply title/abstract screening against inclusion criteria; remove
   duplicates across sources; record screening decisions and exclusion reasons.

4. **Extract evidence**: For included sources, extract: study design, sample characteristics,
   key findings, effect sizes, confidence intervals, and study quality indicators.

5. **Grade evidence**: Apply evidence grading schema (Levels I–V) based on study design
   quality, sample size, and replication status; flag conflicting evidence.

6. **Synthesize and identify gaps**: Summarize findings by theme; compute evidence strength
   per theme; identify gaps — areas with insufficient or conflicting evidence — for
   hypothesis-generation input.

## Output Format

Literature review report with: `research_question`, `sources_searched` (count and list),
`included_studies` (count), `evidence_summary` (by theme with grade), `gaps_identified`
(list with evidence deficit description), and `search_protocol` (reproducibility record).

## References

- `references/literature-review-protocol.md` — search strategy templates, PRISMA checklist, evidence grading schema