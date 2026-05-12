# Adaptive Intake Policy

The orchestrator only re-enters intake (`exploring`) when missing context would materially change the next safe action.

## Rules

1. Prefer draft-first behavior: if enough context exists, produce a draft plan/workflow before asking more.
2. Ask follow-up questions only for unresolved material unknowns.
3. Never re-ask questions recorded in `resolved_questions`.
4. Allow interruption directives (`pause`, `switch`, `forget`) at any point.
5. After explicit correction, transition to the nearest editable state:
   - execution correction -> `creating_workflow`
   - workflow correction -> `refining_plan`
   - otherwise -> `exploring`
