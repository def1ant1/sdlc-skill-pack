# Plan Workspace User Guide

The plan workspace now supports:
- Human-readable plan generation from conversation input.
- Plan Builder sections for objectives, assumptions, phases, tasks, risks, dependencies, and required skills.
- Per-step approvals before execution conversion.
- Living-plan operations: collapse/expand phases, reorder priorities, assumption edits, and step approvals.
- Version history and diff inspection.

## CLI flow
1. Build a plan:
   - `python scripts/orchestration/conversation_to_plan.py --conversation "..." --output runtime/plan.json`
2. Approve plan steps (programmatic APIs in module functions).
3. Convert approved scope:
   - `python scripts/orchestration/plan_to_workflow.py --plan runtime/plan.json --output runtime/workflow.json`
   - `python scripts/orchestration/plan_to_tasks.py --plan runtime/plan.json --output runtime/tasks.json`
