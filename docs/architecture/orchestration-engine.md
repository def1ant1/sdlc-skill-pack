# Orchestration Engine

## Execution model

The graph executor (`scripts/orchestration/execute_graph.py`) executes DAG-style workflow nodes defined by `schemas/workflow-graph.schema.json`.

### Supported runtime semantics

- **Branching:** edges can be conditioned with `when: success` or `when: failure`.
- **Retry semantics:** each node can define `retry.max_attempts`; failed nodes retry until the max is reached.
- **Approvals:** nodes with `approval.required: true` transition to `awaiting_approval` until approval is present in state.
- **Memory hydration:** nodes can declare `memory.requires` and are blocked until required memory keys exist.
- **Evaluator hooks:** execution events can be emitted to evaluator hook registries in `core/evaluator/hooks.py`.
- **Policy enforcement:** governor policy checks in `core/governor/policy.py` can block unsafe/high-impact nodes before execution.
- **Checkpoint/resume:** executor returns serializable `node_states` + `memory`; this output can be passed back as `--state-path` to resume.

### Runtime state transitions

Node statuses include:

- `pending`
- `awaiting_approval`
- `blocked`
- `succeeded`
- `failed`

The state machine is validated by `tests/orchestration/test_execute_graph.py`.

## Conversation orchestration state machine

The conversation orchestrator now includes an explicit user-facing state model implemented in `core/conversation-orchestrator/state_machine.py` with the following states:

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

### Transition inputs

The state machine supports transition updates from:

- Intent cues from user utterances.
- Explicit approval outcomes while awaiting approval.
- Corrections that move to closest editable state.
- Interruptions (`pause`, `switch`, `forget`, `resume`).

### Conversation context tracked

To prevent repetitive intake and support continuity, context tracks:

- Active conversational goal.
- Active artifacts under construction.
- Resolved intake questions.
