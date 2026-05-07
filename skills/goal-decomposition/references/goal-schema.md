# Goal Schema Reference

## Goal Object Format

```yaml
goal:
  id: "GOAL-20260507-001"
  parent_id: null  # null for root goals; parent goal_id for sub-goals
  depth: 0  # 0 = root, 1 = first-level sub-goal, etc.

  statement: "Launch AI-native SDLC platform by Q3 2026"

  smart_criteria:
    specific: "Deploy all 23 SDLC phases to production with ≥ 95% skill coverage"
    measurable: "Measured by: skill_registry_coverage_pct, validation_pass_rate"
    achievable: "Feasibility score: 3/5 — requires 2 additional engineers"
    relevant: "Directly enables strategic objective: AI-native enterprise transformation"
    time_bound: "Deadline: 2026-09-30"

  type: "outcome"  # outcome | milestone | task | constraint

  status: "ACTIVE"  # PENDING | ACTIVE | COMPLETED | BLOCKED | DEFERRED | CANCELLED

  priority: "P1"  # P0 | P1 | P2 | P3

  success_criteria:
    - metric: "skill_registry_coverage_pct"
      threshold: "≥ 95%"
      measurement_method: "validate_skill_structure.py"
    - metric: "validation_pass_rate"
      threshold: "100%"
      measurement_method: "pytest + validate_frontmatter.py"

  dependencies:
    - goal_id: "GOAL-20260507-002"
      type: "finish_to_start"

  resources:
    budget_usd: 500000
    headcount_fte: 4.0
    timeline_days: 144

  metadata:
    created_at: "2026-05-07T00:00:00Z"
    created_by: "goal-decomposition skill"
    last_updated: "2026-05-07T00:00:00Z"
    decomposition_method: "HTN"  # HTN | OKR | SMART | MBO
```

---

## Goal Decomposition Rules

### Rule 1: Decomposability Check

A goal is decomposable if:
1. It cannot be completed by a single agent in a single step
2. It has identifiable sub-components that can be pursued independently
3. It spans more than one planning horizon (sprint, quarter, year)

A goal is atomic (leaf) if it can be assigned to one agent and completed without further breakdown.

### Rule 2: MECE Decomposition

Sub-goals must be **Mutually Exclusive and Collectively Exhaustive**:
- **ME:** No two sub-goals cover the same scope (no duplication of effort)
- **CE:** Completing all sub-goals necessarily achieves the parent goal

```
Verification:
  ME: ∀ i≠j: scope(sub_goal_i) ∩ scope(sub_goal_j) = ∅
  CE: ∪ scope(sub_goals) = scope(parent_goal)
```

### Rule 3: Maximum Depth

```
max_decomposition_depth: 5
# Deeper than 5 levels suggests the goal is too granular for strategic planning
# Leaf goals at depth 5 become tasks in the execution plan
```

### Rule 4: Dependency Graph Constraints

```
# No circular dependencies
ASSERT is_DAG(goal_dependency_graph)

# Maximum fan-in
ASSERT max_dependencies_per_goal ≤ 10

# Critical path identification
critical_path = longest_path(goal_dependency_graph, weight=estimated_duration)
```

---

## Decomposition Strategy Selection

| Parent Goal Characteristics | Recommended Strategy |
|---|---|
| Clear phases or stages | Sequential decomposition |
| Parallel workstreams possible | Parallel decomposition |
| Multiple stakeholder objectives | OKR decomposition |
| Technical system build | Component decomposition |
| Uncertain path to goal | AND-OR tree decomposition |
| Performance improvement | Metric-driven decomposition |

### AND-OR Tree Format

```yaml
and_or_tree:
  root:
    goal_id: "GOAL-001"
    node_type: "AND"  # AND = all children required; OR = any one child sufficient
    children:
      - goal_id: "GOAL-001-A"
        node_type: "AND"
        children: [...]
      - goal_id: "GOAL-001-B"
        node_type: "OR"  # Alternative approaches — pick one
        children:
          - goal_id: "GOAL-001-B-i"
            estimated_cost: 200000
            estimated_duration_days: 30
          - goal_id: "GOAL-001-B-ii"
            estimated_cost: 80000
            estimated_duration_days: 60
```

---

## Goal Validation Checklist

Before finalizing a decomposed goal tree:

```
□ All leaf goals are atomic (achievable by single agent in single step)
□ Decomposition is MECE (no gaps, no overlaps)
□ Dependency graph is acyclic (no circular dependencies)
□ Every goal has measurable success criteria
□ Critical path duration ≤ deadline constraint
□ Resource requirements do not exceed constraints at any time point
□ All goals have assigned owners
□ Risk level assessed for each goal branch
```

---

## Goal Progress Tracking

```yaml
goal_progress:
  goal_id: "GOAL-20260507-001"
  as_of: "2026-05-07T12:00:00Z"

  completion_pct: 42
  sub_goals_total: 12
  sub_goals_completed: 5
  sub_goals_in_progress: 3
  sub_goals_blocked: 1
  sub_goals_not_started: 3

  critical_path_status:
    on_track: true
    projected_completion: "2026-09-15"
    deadline: "2026-09-30"
    buffer_days: 15

  blockers:
    - sub_goal_id: "GOAL-001-C"
      blocking_reason: "Awaiting vendor contract signature"
      escalated_to: "procurement@company.com"
      escalation_date: "2026-05-05"
```