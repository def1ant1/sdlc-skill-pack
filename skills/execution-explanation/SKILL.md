---
name: execution-explanation
description: Generates layered natural-language explanations of workflow executions tailored to the audience — from executive summaries to technical step-by-step traces — drawing on execution lineage and causal traces.
metadata:
  version: "1.0.0"
  category: explainability
  owner: platform
  maturity: alpha
  dependencies: [explainability, causal-tracing, telemetry]

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

Audience-adaptive explanation generator for the explainability runtime. Translates raw
execution logs, causal traces, and workflow records into clear, layered natural-language
explanations calibrated to the technical depth appropriate for the requesting audience —
from board-level summaries to developer-grade step traces.

## Activation Triggers

- Operator requests an explanation of a completed or in-progress workflow execution
- Governance audit requires natural-language documentation of an AI decision
- hitl-dashboard escalation requires context explanation for a human reviewer
- Post-incident review requires human-readable execution narrative

## Execution Protocol

1. **Identify audience tier**: Classify the requester — Executive (non-technical summary),
   Manager (outcome + key decisions), Analyst (methodology + data), or Engineer (full
   step-by-step trace with inputs/outputs).

2. **Load execution record**: Retrieve the workflow execution log, causal trace (if available),
   checkpoint history, and any decisions made by the AI during execution.

3. **Extract key narrative elements**: Identify the objective, key decisions and their
   rationale, significant outputs, exceptions encountered, and overall outcome.

4. **Generate layered explanation**: Produce explanation at the appropriate depth tier;
   include drill-down links to more detailed layers for human readers.

5. **Render supporting visualizations**: If audience tier is Analyst or Engineer, request
   reasoning-visualization to produce supplementary goal tree or execution flow diagram.

6. **Deliver and log**: Return the explanation document; log the explanation request and
   delivery for auditability.

## Output Format

Explanation document with: `audience_tier`, `workflow_id`, `executive_summary` (2–3 sentences),
`key_decisions` (list with rationale), `outcome_statement`, and optionally `detailed_trace`
(step-by-step) and `visualization_reference` for Engineer/Analyst tiers.

## References

- `references/explanation-templates.md` — audience tier definitions, narrative templates, drill-down link format