---
name: explainability
description: Generates human-readable explanations of autonomous decisions, traces causal reasoning chains, produces execution lineage reports, and supports governance accountability requirements.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [knowledge-graph, cognitive-runtime, governance, telemetry]
---

## Role

Explainability and causal transparency layer for the Autonomous OS. Reconstructs the reasoning
chain behind any autonomous decision, traces execution lineage from objective to outcome, and
produces governance-grade explanation artifacts for operators, auditors, and regulators.

## Activation Triggers

- Operator requests explanation of a specific autonomous decision
- Governance audit requires reasoning trace for compliance documentation
- HITL intervention requires context about what the OS was doing and why
- Compliance review of an autonomous action
- Stakeholder briefing requiring accessible explanation of AI behavior

## Execution Protocol

1. **Identify explanation target**: Parse the explanation request — decision-id, workflow-id,
   or action-id — and determine the required audience (operator, executive, auditor, regulator).

2. **Reconstruct reasoning chain**: Retrieve goal tree, plan, evidence used, intermediate
   conclusions, and constraints from the knowledge graph.

3. **Trace execution lineage**: Map each action in the workflow to its triggering goal, plan
   step, responsible agent, and approval events.

4. **Identify key decision factors**: Rank evidence, constraints, and assumptions by causal
   contribution to the final decision; surface the top factors.

5. **Generate layered explanation**: Produce audience-appropriate explanation — executive
   summary (3 sentences), technical narrative (step-by-step reasoning), and supporting evidence
   appendix.

6. **Attach audit artifact**: Write explanation record to governance log with immutable
   timestamp and link to original decision/workflow record.

## Output Format

Layered explanation document with: executive summary, technical narrative, decision factor
ranking, supporting evidence, execution lineage diagram reference, and audit record ID.

## References

- `references/explanation-formats.md` — explanation schemas for executive, technical, and regulatory audiences; lineage graph format