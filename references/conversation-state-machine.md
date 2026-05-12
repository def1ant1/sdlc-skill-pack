# Conversation State Machine

Defines explicit conversational states for orchestration:

- `idle`
- `exploring`
- `drafting_plan`
- `refining_plan`
- `creating_workflow`
- `executing_workflow`
- `awaiting_approval`
- `curating_knowledge`
- `scheduling_task`
- `reviewing_results`

## Transition drivers

Transitions are triggered by:

1. User utterance intent signals.
2. Approval outcomes (`approved=true|false`) while awaiting approval.
3. Corrections from the user while drafting/creating/executing.
4. Interruptions:
   - `pause`: park current state and move to `idle`
   - `switch`: move to `exploring`
   - `forget`: clear goal/artifacts/resolved questions and move to `idle`
   - `resume`: restore parked state

## Conversation memory fields

- `goal`: current conversational objective.
- `active_artifacts`: currently edited/produced artifacts.
- `resolved_questions`: prior intake questions already answered, preventing repetitive intake loops.
