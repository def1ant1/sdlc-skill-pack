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
