# Workflow Replay Protocol Reference

## Replay Modes

| Mode | Code | Purpose | Determinism Required | Side Effects |
|---|---|---|---|---|
| Audit replay | RP-AUD | Reproduce exact execution for audit/compliance | Strict | None (read-only) |
| Debug replay | RP-DBG | Step through execution with pause points | Strict | None (dry-run) |
| Recovery replay | RP-REC | Resume from checkpoint after failure | From checkpoint | Allowed (idempotent) |
| Counterfactual replay | RP-CF | What-if replay with modified inputs | None (exploration) | None |
| Performance replay | RP-PERF | Re-execute to benchmark with different model | None | None |

---

## Replay Preconditions

```
FUNCTION validate_replay_eligibility(workflow_id, replay_mode):
    # Fetch original execution record
    original = execution_store.get(workflow_id)

    # Checkpoint availability
    IF replay_mode == RP-REC:
        ASSERT original.has_valid_checkpoint
        ASSERT original.checkpoint.integrity_check() == PASS

    # Input immutability check
    IF replay_mode IN [RP-AUD, RP-DBG]:
        FOR each input_ref IN original.input_refs:
            current_hash = hash_content(resolve(input_ref))
            ASSERT current_hash == original.input_hashes[input_ref]
            # If inputs changed → cannot guarantee faithful replay

    # Model availability
    ASSERT model_registry.is_available(original.model_id, original.model_version)
    # If original model unavailable: replay_mode must be RP-CF or RP-PERF

    # Dependency state
    FOR each external_call IN original.external_calls:
        IF external_call.is_deterministic == false AND replay_mode == RP-AUD:
            FLAG as REPLAY_DIVERGENCE_RISK
```

---

## Determinism Controls

### Seed Management

```yaml
determinism_config:
  random_seed: 42  # Fixed seed for all stochastic operations
  model_temperature: 0.0  # Greedy decoding for strict reproducibility
  model_top_p: null  # Disable nucleus sampling in audit mode
  model_top_k: null  # Disable top-k sampling in audit mode

  # For models that don't support deterministic inference:
  fallback_strategy: "store_and_replay_outputs"
  # Store original outputs; replay uses stored outputs instead of re-generating
```

### Non-Deterministic Element Handling

```
Non-deterministic elements and their replay treatment:

CURRENT_TIMESTAMP:
  → Substitute: original_timestamp[step_id]
  → Policy: Never use live timestamp in replay (except RP-CF for testing)

RANDOM_NUMBER_GENERATION:
  → Substitute: stored_rng_state[step_id] (replay RNG from recorded seed)

EXTERNAL_API_CALLS:
  → Substitute: stored_response[call_id] (cached response from original execution)
  → Exception: RP-REC mode may re-execute idempotent APIs if cache missing

MODEL_INFERENCE (non-zero temperature):
  → Substitute: stored_model_output[step_id]
  → Verify: hash(stored_output) == original_output_hash[step_id]
```

---

## Step-by-Step Replay Protocol

```
PROCEDURE replay_workflow(workflow_id, replay_mode, replay_config):

  STEP 1: Load execution manifest
    manifest = execution_store.get_manifest(workflow_id)
    steps = manifest.steps_in_order()
    start_step = get_start_step(replay_mode, manifest)

  STEP 2: Initialize replay environment
    env = ReplayEnvironment(
        mode=replay_mode,
        input_overrides=replay_config.input_overrides,  # For RP-CF
        stored_outputs=manifest.stored_outputs,
        model_version_override=replay_config.model_version  # For RP-PERF
    )

  STEP 3: Execute steps
    FOR each step s IN steps starting from start_step:

      # Load stored inputs for this step
      step_inputs = env.resolve_inputs(s.input_refs)

      # Compute expected output hash (for audit comparison)
      expected_hash = manifest.output_hashes[s.id]

      # Execute step
      IF replay_mode == RP-AUD AND s.is_non_deterministic:
          # Use stored output; do not re-execute
          actual_output = env.load_stored_output(s.id)
      ELSE:
          actual_output = s.execute(step_inputs, env.determinism_config)

      # Verify output (for RP-AUD and RP-DBG)
      IF replay_mode IN [RP-AUD, RP-DBG]:
          actual_hash = hash(actual_output)
          IF actual_hash != expected_hash:
              RECORD DivergenceEvent(step=s, expected=expected_hash, actual=actual_hash)

      # Pause point (RP-DBG only)
      IF replay_mode == RP-DBG AND s.id IN replay_config.pause_points:
          EMIT PauseEvent(step=s, output=actual_output)
          AWAIT resume_signal()

  STEP 4: Generate replay report
    RETURN ReplayReport(
        workflow_id=workflow_id,
        replay_mode=replay_mode,
        steps_replayed=len(steps),
        divergences=env.divergence_log,
        verdict=PASS if not env.divergence_log else DIVERGED
    )
```

---

## Divergence Classification

| Divergence Type | Code | Severity | Meaning |
|---|---|---|---|
| Output hash mismatch | DIV-HASH | CRITICAL | Exact replay differs from original |
| Non-deterministic expected | DIV-ND | INFO | Expected divergence (RNG, timestamps) |
| Missing stored output | DIV-MISS | HIGH | Replay cannot proceed without stored output |
| Input modified | DIV-INPUT | CRITICAL | Input data changed since original execution |
| Model version changed | DIV-MODEL | HIGH | Different model may produce different output |

---

## Replay Record Format

```yaml
replay_record:
  replay_id: "RPL-20260507-001"
  original_workflow_id: "WF-20260501-042"
  replay_mode: "RP-AUD"
  initiated_by: "compliance-auditor@company.com"
  initiated_at: "2026-05-07T10:00:00Z"
  completed_at: "2026-05-07T10:04:32Z"

  steps_replayed: 12
  steps_passed: 12
  steps_diverged: 0
  divergences: []

  verdict: "EXACT_MATCH"  # EXACT_MATCH | DIVERGED | PARTIAL (RP-REC only)
  certified_by_compliance: false  # Set to true after compliance officer review

  immutable_hash: "sha256:a3f8c2..."  # Hash of this replay record itself
```