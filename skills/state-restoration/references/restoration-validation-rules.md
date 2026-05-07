# State Restoration Validation Rules Reference

## Restoration Validation Framework

State restoration is valid only when the restored state is **consistent**, **complete**, and **safe to resume** from.

### Consistency

The restored state must satisfy all invariants that held before the interruption:

```
CONSISTENCY INVARIANTS:
  INV-1: All referenced entities still exist
    FOR each entity_ref IN state.entity_references:
      ASSERT entity_store.exists(entity_ref.id)
      ASSERT entity_store.version(entity_ref.id) == entity_ref.expected_version

  INV-2: No partial writes committed
    ASSERT state.in_flight_transactions == []
    # If partial transaction: must rollback before restoring

  INV-3: Causal ordering preserved
    FOR each event e IN state.event_log:
      ASSERT e.sequence_number == expected_sequence_number++

  INV-4: Resource locks released
    FOR each lock l IN state.held_locks:
      IF lock_manager.is_held_by_other(l.resource):
        FAIL restoration_with("Lock conflict: " + l.resource)
```

### Completeness

```
COMPLETENESS CHECKS:
  CP-1: All required checkpoint fields present
    required_fields = [
      "workflow_id", "step_id", "step_index", "state_snapshot",
      "input_checksums", "output_checksums", "timestamp", "integrity_hash"
    ]
    FOR each field IN required_fields:
      ASSERT field IN checkpoint

  CP-2: State snapshot covers all workflow variables
    FOR each variable v IN workflow.declared_variables:
      ASSERT v IN checkpoint.state_snapshot

  CP-3: Output completeness from completed steps
    FOR each completed_step s with index < checkpoint.step_index:
      ASSERT checkpoint.output_checksums[s.id] != null
```

### Safety

```
SAFETY CHECKS:
  SF-1: Checkpoint has not expired
    ASSERT current_time - checkpoint.timestamp < retention_policy.max_age

  SF-2: Integrity hash valid
    computed_hash = SHA256(serialize(checkpoint without integrity_hash field))
    ASSERT computed_hash == checkpoint.integrity_hash

  SF-3: No external side effects to re-execute
    FOR each completed_step s with index < checkpoint.step_index:
      IF s.has_external_side_effects:
        ASSERT s.is_idempotent OR s.side_effects_recorded_for_replay
        # Non-idempotent external calls cannot be safely re-executed

  SF-4: Authorization still valid
    ASSERT authorization_service.is_valid(checkpoint.auth_token)
    ASSERT checkpoint.executor_permissions == current_permissions

  SF-5: Environmental compatibility
    ASSERT checkpoint.runtime_version compatible_with current_runtime_version
    ASSERT all checkpoint.dependencies_versions still_available
```

---

## Restoration Decision Matrix

| INV Failures | CP Failures | SF Failures | Decision | Action |
|---|---|---|---|---|
| 0 | 0 | 0 | RESTORE | Resume from checkpoint |
| 0 | 0 | SF-1 only | RESTORE_WITH_WARNING | Resume; flag expired checkpoint |
| 0 | 0 | SF-3 (idempotent) | RESTORE_WITH_REPLAY | Replay idempotent side effects |
| 0 | 0 | SF-3 (non-idempotent) | ESCALATE | Human review required |
| 1+ | 0 | 0 | REBUILD | Re-execute from last valid checkpoint |
| 0 | 1+ | 0 | REBUILD | Re-execute from last valid checkpoint |
| Any | Any | SF-2 (hash fail) | REJECT | Checkpoint corrupted; cannot use |
| Any | Any | SF-4 (auth expired) | REJECT | Re-authorization required |

---

## Restoration Protocol

```
PROCEDURE restore_workflow(workflow_id, checkpoint_id):

  STEP 1: Load checkpoint
    checkpoint = checkpoint_store.get(checkpoint_id)
    IF NOT checkpoint:
        RETURN FAIL("Checkpoint not found")

  STEP 2: Run validation rules
    consistency_result = validate_consistency(checkpoint)
    completeness_result = validate_completeness(checkpoint)
    safety_result = validate_safety(checkpoint)

    decision = decision_matrix(consistency_result, completeness_result, safety_result)

  STEP 3: Apply decision
    IF decision == RESTORE:
        state = deserialize(checkpoint.state_snapshot)
        resume_from_step(workflow_id, checkpoint.step_id, state)

    ELIF decision == RESTORE_WITH_WARNING:
        LOG_WARNING("Restoring from expired checkpoint: " + checkpoint_id)
        state = deserialize(checkpoint.state_snapshot)
        resume_from_step(workflow_id, checkpoint.step_id, state)

    ELIF decision == RESTORE_WITH_REPLAY:
        state = deserialize(checkpoint.state_snapshot)
        replay_idempotent_side_effects(checkpoint)
        resume_from_step(workflow_id, checkpoint.step_id, state)

    ELIF decision == REBUILD:
        last_valid = find_last_valid_checkpoint(workflow_id, before=checkpoint_id)
        IF last_valid:
            restore_workflow(workflow_id, last_valid.id)  # Recurse
        ELSE:
            restart_workflow_from_beginning(workflow_id)

    ELIF decision == ESCALATE:
        notify_human_review(workflow_id, checkpoint_id, safety_result)
        pause_workflow(workflow_id)

    ELIF decision == REJECT:
        LOG_ERROR("Checkpoint rejected: " + str(safety_result.failures))
        RETURN FAIL("Cannot restore: " + safety_result.failure_reason)
```

---

## Post-Restoration Verification

After restoring and resuming, verify the resumed execution is on the expected path:

```yaml
post_restoration_checks:
  - check: "First completed step after restoration matches expected output"
    method: "compare_output_hash_to_checkpoint_expectation"
    on_fail: "PAUSE and alert — possible state corruption"

  - check: "No duplicate side effects (idempotency verification)"
    method: "check_external_system_state_vs_checkpoint_record"
    on_fail: "LOG and continue — idempotent systems tolerate duplicates"

  - check: "Workflow progression is monotonically increasing"
    method: "assert step_index_after > step_index_at_checkpoint"
    on_fail: "HALT — infinite loop suspected"
```

---

## Restoration Audit Log

```yaml
restoration_event:
  event_id: "RST-20260507-001"
  workflow_id: "WF-20260507-042"
  checkpoint_id: "CHK-20260507-042-003"
  restored_at: "2026-05-07T14:30:00Z"
  restored_by: "runtime-recovery skill"

  validation_results:
    consistency: PASS
    completeness: PASS
    safety: PASS_WITH_WARNING  # SF-1: checkpoint age = 2h (limit = 24h)

  decision: RESTORE_WITH_WARNING
  resumed_from_step: "step-008-validate-output"
  steps_skipped: 7  # Steps 1-7 already completed before interruption

  outcome: "WORKFLOW_COMPLETED_SUCCESSFULLY"
  total_additional_time_seconds: 145
```