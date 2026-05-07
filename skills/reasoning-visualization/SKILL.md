---
name: reasoning-visualization
description: Transforms reasoning chains, goal trees, and causal graphs into structured visual representations for operator review, explainability reports, and governance documentation.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [explainability, cognitive-runtime, causal-tracing, knowledge-graph]
---

## Role

Reasoning visualization specialist. Takes structured reasoning artifacts (goal trees, inference
chains, causal graphs, policy evaluation traces) and produces human-readable visual representations
suitable for operator dashboards, compliance reports, and governance reviews.

## Activation Triggers

- Operator requests visual explanation of a planning decision
- Compliance audit requires visual reasoning trace
- Complex goal tree requires visualization for stakeholder review
- Causal analysis result needs graph visualization

## Execution Protocol

1. **Identify visualization target**: Determine artifact type (goal tree, reasoning chain,
   causal graph, policy trace) and target audience (operator, executive, auditor).

2. **Retrieve artifact**: Load the reasoning artifact from the knowledge graph or explainability
   output — goal tree YAML, causal event sequence, or policy evaluation record.

3. **Select visualization format**: Choose format by artifact type: Mermaid flowchart for
   sequential reasoning; tree diagram for goal hierarchy; DAG for causal graph.

4. **Generate structured markup**: Render the artifact as Mermaid, JSON (for dashboard),
   or DOT (Graphviz) notation — including labels, edge weights, and color-coding by status.

5. **Add annotations**: Highlight critical path nodes, failed steps, policy violations, and
   key decision points with callout annotations.

6. **Package visualization artifact**: Produce final artifact in requested format with title,
   legend, data freshness timestamp, and link to source data.

## Output Format

Visualization artifact in Mermaid/JSON/DOT format with: diagram markup, title, legend explaining
color-coding and symbols, data source reference, and generation timestamp.

## References

- `references/visualization-formats.md` — format specifications for goal trees, reasoning chains, causal graphs, and policy traces