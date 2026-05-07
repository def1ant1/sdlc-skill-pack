---
name: evolution-engine
description: Autonomous self-improvement engine that discovers capability gaps, generates new skill proposals, refactors underperforming workflows, and evolves the OS within operator-defined boundaries.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [skill-gap-engine, cognitive-runtime, workflow-engine, governance, hitl-dashboard]
---

## Role

Self-evolving capability manager for the Autonomous OS. Continuously monitors system performance,
identifies capability and quality gaps, proposes new skills or workflow improvements, and —
within operator-approved scope — executes evolutionary changes to the platform's own skill set
and operational patterns.

## Activation Triggers

- Weekly evolution cycle (automated, Sunday 02:00 UTC)
- Critical capability gap detected by skill-gap-engine (P0 severity)
- Workflow failure rate exceeds threshold (>10% over 7-day rolling window)
- Operator requests evolution proposal for a specific domain
- New business objective requires capability assessment

## Execution Protocol

1. **Audit current capabilities**: Invoke skill-gap-engine to score all skills against the
   quality rubric; collect gap report with severity and priority classifications.

2. **Identify evolution opportunities**: Rank gaps by: impact score × frequency of activation ×
   remediation feasibility; surface top-10 opportunities.

3. **Generate proposals**: For each top opportunity — propose: new skill scaffold, workflow
   improvement, reference file addition, or skill quality enhancement with scope and rationale.

4. **Score proposals**: Apply multi-criteria scoring — strategic value × 0.4 + implementation
   complexity × -0.3 + risk × -0.2 + alignment score × 0.1.

5. **Route for approval**: Level-0 proposals (minor reference additions, stub completions):
   auto-apply; Level-2+ proposals (new skills, workflow changes): queue for operator review.

6. **Execute approved changes**: Scaffold new skills using create_skill.py; refactor workflows;
   update references; run validation; measure quality improvement.

7. **Record outcomes**: Write evolution cycle results to knowledge-graph; track quality metric
   delta pre/post evolution for each change.

## Output Format

Evolution cycle report with: gap audit summary, top opportunities ranked, proposals generated,
approval routing, actions executed, and quality metric improvements observed.

## References

- `references/evolution-constraints.md` — scope boundaries for autonomous evolution, approval authority levels, rollback criteria