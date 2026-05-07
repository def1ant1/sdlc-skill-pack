---
name: checkpoint-management
description: Serializes and persists workflow execution state to durable storage at configurable intervals, enabling resumable workflows and point-in-time recovery after failures.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [workflow-runtime, event-bus, telemetry]
---

## Role

Checkpoint lifecycle manager for the durable workflow runtime. Captures consistent snapshots
of workflow execution state at configurable intervals, writes them to durable storage with
integrity protection, and maintains the checkpoint registry for recovery and replay operations.

## Activation Triggers

- Workflow step completes successfully (checkpoint after every step by default)
- Configurable checkpoint interval elapses during a long-running step
- Manual checkpoint requested by operator or workflow definition
- Workflow failure detected requiring pre-failure state preservation

## Execution Protocol

1. **Capture state snapshot**: Serialize the full workflow context — step index, variable
   bindings, pending task queue, completed step registry, and actor session state.

2. **Compute integrity hash**: Calculate SHA-256 of the serialized state payload for tamper
   detection and corruption identification during recovery.

3. **Write to durable store**: Persist checkpoint payload with all metadata to the configured
   backend (Redis for active, PostgreSQL for warm, S3 for archival).

4. **Register checkpoint**: Record checkpoint-id, workflow-id, step-index, timestamp, storage
   location, and integrity hash in the checkpoint registry.

5. **Prune old checkpoints**: Apply retention policy — retain last N checkpoints per workflow;
   delete older ones; always keep the final checkpoint of completed workflows.

6. **Emit event**: Publish `checkpoint.created` event with checkpoint-id, size, storage
   backend, and creation latency for telemetry.

## Output Format

Checkpoint registration record with: `checkpoint_id`, `workflow_id`, `step_index`,
`storage_backend`, `storage_key`, `state_hash`, `payload_hash`, `size_bytes`, `created_at`,
and `compression_algorithm`.

## References

- `references/checkpoint-schema.md` — checkpoint payload format, storage backends, retention policy, idempotency protocol