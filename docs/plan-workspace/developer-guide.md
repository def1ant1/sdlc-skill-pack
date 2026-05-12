# Plan Workspace Developer Guide

## New orchestration modules
- `scripts/orchestration/conversation_to_plan.py`
  - `conversation_to_plan()` pipeline outputting human-readable structured plans first.
  - Living operations: `collapse_expand_section`, `reorder_priorities`, `edit_assumptions`, `approve_step`, `version_diff_history`.
- `scripts/orchestration/plan_to_workflow.py`
  - Converts only approved plan steps into workflow format.
- `scripts/orchestration/plan_to_tasks.py`
  - Converts only approved plan steps into task list format.

## Design notes
- Plan model is dataclass-based (`LivingPlan`, `PlanPhase`, `PlanStep`) to keep mutation logic explicit.
- All living operations increment `version` and append immutable history entries.
- Downstream conversion intentionally filters to `status == approved` to enforce HITL boundaries.
