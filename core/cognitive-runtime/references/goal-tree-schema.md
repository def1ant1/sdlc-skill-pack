# Goal Tree Schema

## Overview

The goal tree is the primary planning artifact produced by `cognitive-runtime`. It represents
a hierarchical decomposition of an objective into sub-goals and atomic actions.

---

## Goal Node Structure

```yaml
goal:
  id: "GOAL-YYYYMMDD-NNN"
  type: "objective | sub-goal | task | action"
  title: "<concise goal statement>"
  description: "<detailed description with success criteria>"
  owner: "<skill name or agent id>"
  status: "pending | in-progress | blocked | completed | cancelled"
  priority: "P0 | P1 | P2 | P3"
  deadline: "YYYY-MM-DD"
  confidence: 0.0–1.0          # planner confidence this goal is achievable
  parent_id: "GOAL-YYYYMMDD-NNN | null"
  children: ["GOAL-...", ...]
  dependencies: ["GOAL-...", ...]  # goals that must complete before this can start
  constraints: ["<constraint text>", ...]
  success_criteria:
    - metric: "<measurement>"
      threshold: "<target value>"
  created_at: "ISO8601"
  updated_at: "ISO8601"
```

---

## Goal Type Hierarchy

```
objective          # Top-level intent (e.g., "Launch v2.0 by Q3")
  └─ sub-goal      # Major deliverable (e.g., "Complete backend services")
       └─ task     # Assignable work unit (e.g., "Implement auth API")
            └─ action  # Atomic executable step (e.g., "Write JWT middleware")
```

**Decomposition rules:**
- An `objective` must have ≥ 2 `sub-goal` children
- A `sub-goal` must have ≥ 1 `task` child
- A `task` may have `action` children or be atomic itself
- `action` nodes have no children; they map directly to skill invocations

---

## Serialization Format

Goal trees are serialized as YAML files and stored in the knowledge graph as `Plan` nodes.

```yaml
goal_tree:
  root_id: "GOAL-20260507-001"
  created_at: "2026-05-07T00:00:00Z"
  workflow_id: "WF-20260507-001"
  version: "1"
  nodes:
    - id: "GOAL-20260507-001"
      type: objective
      title: "Launch v2.0 platform"
      owner: sdlc-orchestration
      deadline: "2026-09-30"
      children: ["GOAL-20260507-002", "GOAL-20260507-003"]
      dependencies: []
    - id: "GOAL-20260507-002"
      type: sub-goal
      title: "Complete backend services"
      parent_id: "GOAL-20260507-001"
      owner: backend-engineering
      children: ["GOAL-20260507-004"]
      dependencies: []
    - id: "GOAL-20260507-004"
      type: task
      title: "Implement auth API"
      parent_id: "GOAL-20260507-002"
      owner: backend-engineering
      children: []
      dependencies: []
      success_criteria:
        - metric: "unit test coverage"
          threshold: ">= 90%"
```

---

## Status Transitions

```
pending → in-progress → completed
pending → blocked      (dependency not met)
in-progress → blocked  (unexpected blocker)
blocked → in-progress  (blocker resolved)
any → cancelled        (scope change or superseded)
```

Blocked goals emit `goal.blocked` events to event-bus with the blocking dependency id.
Completed goals emit `goal.completed` events that trigger downstream dependency resolution.

---

## Critical Path Computation

The critical path is the longest dependency chain from root to a leaf action. It determines
the minimum time-to-completion for the objective.

**Algorithm:**
1. Build a DAG from goal nodes and their `dependencies`
2. Topological sort the DAG
3. Compute earliest-start and latest-start for each node (CPM forward/backward pass)
4. Flag nodes where slack = 0 as on the critical path

Critical path nodes receive `priority: P0` override regardless of their initial priority.

---

## Knowledge Graph Integration

Goal trees are written to the knowledge graph as:

| Node Type | Entity |
|---|---|
| `Plan` | Root goal tree node |
| `Task` | Sub-goal and task nodes |
| `Decision` | Nodes where strategy was chosen |

Relationships: `Plan -[CONTAINS]-> Task`, `Task -[DEPENDS_ON]-> Task`, `Plan -[ADDRESSES]-> objective_text`