---
name: state-restoration
description: Restores workflow execution context from a valid checkpoint, verifying integrity and reconstructing all variable bindings, pending tasks, and actor state before resuming.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [checkpoint-management, workflow-runtime, telemetry]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Specialized state reconstruction engine for the durable workflow runtime. Given a checkpoint
ID, restores the full workflow execution context — variable bindings, pending task queue,
completed step registry, and actor state — with integrity verification at every stage.

## Activation Triggers

- Runtime-recovery requests state restoration from a specific checkpoint
- Workflow-replay initializes a replay session from a historical checkpoint
- Manual state inspection requested by an operator for debugging
- State migration between storage backends required

## Execution Protocol

1. **Load checkpoint**: Retrieve checkpoint payload from the storage backend specified in the
   checkpoint registry; verify that the checkpoint exists and is not marked as corrupt.

2. **Verify integrity**: Compute SHA-256 of the retrieved payload and compare to the stored
   `payload_hash`; if mismatch, flag as corrupt and abort with `state.integrity_failure`.

3. **Decompress payload**: If compressed (zstd), decompress the serialized state blob.

4. **Deserialize context**: Reconstruct workflow context: variable bindings, completed step
   list, pending task queue, and actor session state from the serialized representation.

5. **Validate context schema**: Ensure all required workflow context fields are present and
   types match the workflow definition schema; flag any schema mismatches.

6. **Register restored context**: Write the restored context back into the active workflow
   state store; emit `state.restored` event with checkpoint ID, step index, and restoration latency.

## Output Format

Restored workflow execution context object containing: `workflow_id`, `step_index`,
`variables` map, `completed_steps` list, `pending_tasks` list, `restored_from_checkpoint_id`,
`integrity_verified: true`, and `restoration_latency_ms`.

## References

- `references/restoration-validation-rules.md` — context schema validation rules and integrity verification procedures