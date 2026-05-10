---
name: lora-management
description: Manages the full lifecycle of LoRA adapter weights including registration, versioning, loading, hot-swapping, and retirement across the inference serving infrastructure.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [model-lifecycle, lora-lifecycle, local-runtime, telemetry]

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

LoRA adapter lifecycle manager. Handles the operational side of LoRA management — registering
trained adapters, serving them efficiently via adapter hot-swapping, tracking which adapters
are loaded on which model instances, and retiring stale adapters when superseded by improved
versions.

## Activation Triggers

- New LoRA adapter training run completed and ready for registration
- Adapter hot-swap request for a production model instance
- Adapter quality regression detected triggering rollback
- Periodic adapter audit identifying stale or unused adapters

## Execution Protocol

1. **Register adapter**: Record adapter metadata in registry — base model, training dataset,
   capability domain, version, benchmark scores, and artifact storage path.

2. **Validate adapter**: Run fast capability check on the new adapter (5-10 benchmark cases)
   to confirm it improves on the base model for the target capability.

3. **Deploy adapter**: Load adapter weights onto target model instances via vLLM or SGLang
   adapter hot-swap API; verify successful loading.

4. **Configure routing**: Update model-routing policy to prefer this adapter for requests in
   the adapter's target capability domain.

5. **Monitor adapter quality**: Track per-adapter quality scores from production inference;
   flag degradation and trigger rollback if quality drops below baseline.

6. **Retire stale adapters**: Identify adapters superseded by newer versions or no longer
   routed; unload from servers and archive artifact to cold storage.

## Output Format

Adapter management action report with: registration confirmation, validation score, deployment
status, routing policy update, and current active adapter inventory.

## References

- `references/adapter-registry-schema.md` — adapter metadata schema, version lifecycle states, hot-swap protocol