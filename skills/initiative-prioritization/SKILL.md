---
name: initiative-prioritization
description: Applies weighted multi-criteria ranking to a set of candidate initiatives, resolves priority conflicts, and produces a recommended execution sequence aligned with strategic objectives and capacity constraints.
metadata:
  version: "1.0.0"
  category: governance
  owner: strategy
  maturity: alpha
  dependencies: [portfolio-optimization, capacity-balancing, telemetry]
---

## Role

Weighted multi-criteria initiative ranking engine for the PMO. Systematically evaluates and
ranks candidate initiatives — from backlogs, stakeholder requests, or strategic plans — against
a consistent scoring framework, resolving priority conflicts and producing a sequenced execution
recommendation aligned with capacity.

## Activation Triggers

- Portfolio-optimization requires a prioritized initiative list for allocation optimization
- New initiative submitted requiring comparative ranking against the existing backlog
- Operator requests re-prioritization following a strategic objective change
- Capacity-balancing identifies a resourcing window that can absorb a deferred initiative

## Execution Protocol

1. **Normalize initiative descriptions**: Ensure each candidate initiative has: objective,
   expected benefit (qualitative and quantitative), required resources (budget, headcount,
   duration), strategic objective alignment tags, and dependencies on other initiatives.

2. **Apply scoring criteria**: Score each initiative on: strategic alignment (30%), business
   value (25%), urgency and time-sensitivity (20%), risk (15%), and implementation feasibility (10%).

3. **Compute weighted rank**: Calculate the weighted composite score for each initiative;
   normalize to a 0–100 priority score.

4. **Resolve conflicts**: Identify priority ties and resolve by secondary criteria (urgency
   as tiebreaker); surface initiatives with conflicting stakeholder priority signals for
   human resolution.

5. **Apply capacity sequencing**: Given the available capacity profile over the planning
   horizon, sequence high-priority initiatives that fit within capacity; surface initiatives
   that must wait for capacity.

6. **Produce ranked backlog**: Return the prioritized and sequenced initiative list with
   scores, rationale, and recommended start windows.

## Output Format

Prioritized initiative list with: `ranking_date`, each initiative with `priority_score`,
`rank`, `scoring_breakdown` (per criterion), `recommended_start_window`, `conflicts_flagged`
(list), and `deferred_initiatives` with deferral reason.

## References

- `references/prioritization-criteria.md` — scoring criterion definitions, weight table, conflict resolution rules