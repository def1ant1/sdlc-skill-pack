# LoRA Adapter Registry Schema Reference

## Registry Entry Schema

```yaml
lora_adapter:
  # Identity
  adapter_id: "LORA-CODE-PYTHON-V3-20260507"
  name: "Python Code Generation Specialist"
  version: "3.0.0"
  created_at: "2026-05-07T00:00:00Z"
  created_by: "ml-platform-team"

  # Base model
  base_model:
    model_id: "standard-local-002"
    model_family: "llama"
    model_size_b: 13  # Billion parameters
    base_model_version: "13B-chat-v2.1"
    architecture: "transformer-decoder"

  # LoRA configuration
  lora_config:
    rank: 16  # LoRA rank r (higher = more parameters, more capacity)
    alpha: 32  # Scaling factor α (alpha/rank = effective learning rate scale)
    dropout: 0.05
    target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
    # q/k/v/o = attention projection layers; adding gate/up/down covers MLP too
    bias: "none"  # "none" | "all" | "lora_only"

  # Trainable parameters
  parameters:
    adapter_parameters: 6815744  # ~6.8M trainable params
    base_model_parameters: 13000000000  # 13B frozen
    adapter_fraction_pct: 0.052  # 0.052% of total parameters

  # Training provenance
  training:
    dataset_id: "SYNTH-PYTHON-CODE-V2"
    training_examples: 45000
    epochs: 3
    learning_rate: 2e-4
    batch_size: 32
    training_duration_hours: 8.4
    training_compute: "4× A100 80GB"

  # Capability profile
  capability_profile:
    target_domain: "python_code_generation"
    target_task_types: ["code_generation_simple", "code_generation_complex", "code_explanation"]
    capability_improvement_vs_base:
      code_generation_python: +12.3  # Points improvement on benchmark
      code_generation_javascript: -1.2  # Slight degradation (acceptable)
      summarization: -0.8  # Negligible degradation

  # Quality gates (must all pass for registry entry)
  quality_gates:
    benchmark_improvement: true  # Adapter improves on target task
    regression_check_passed: true  # No significant regression on non-target tasks
    alignment_check_passed: true  # All alignment test suites pass
    deployment_test_passed: true  # Successful test inference run

  # Lifecycle
  lifecycle:
    status: "ACTIVE"  # DRAFT | STAGED | ACTIVE | DEPRECATED | RETIRED
    promoted_to_active: "2026-05-07T12:00:00Z"
    promoted_by: "ml-governance-committee"
    deprecation_date: null
    retirement_date: null
    successor_adapter_id: null  # Filled when deprecated
```

---

## Registry Query API

### Find adapters by task type

```python
def find_adapters(task_type, base_model_id, min_improvement=5.0):
    """
    Find LoRA adapters that improve on the given task type.
    Returns adapters sorted by improvement descending.
    """
    return registry.query(
        filter={
            "lifecycle.status": "ACTIVE",
            "base_model.model_id": base_model_id,
            "capability_profile.target_task_types": {"$contains": task_type},
            f"capability_profile.capability_improvement_vs_base.{task_type}": {"$gte": min_improvement}
        },
        sort_by=f"capability_profile.capability_improvement_vs_base.{task_type}",
        order="descending"
    )
```

### Adapter compatibility check

```python
def is_compatible(adapter, target_model):
    """
    Check if a LoRA adapter can be applied to a target base model.
    LoRA adapters are tied to specific base model architectures.
    """
    return (
        adapter.base_model.model_family == target_model.model_family
        and adapter.base_model.model_size_b == target_model.model_size_b
        and adapter.base_model.architecture == target_model.architecture
        and adapter.lora_config.target_modules
            <= set(target_model.available_modules)
    )
```

---

## Adapter Composition Rules

### Rule 1: Single-Adapter Default

```
Default: apply at most one LoRA adapter per request.
Reason: Multiple adapters may interfere unless explicitly designed for composition.
```

### Rule 2: Multi-Adapter (LoRA-MoE)

When multiple adapters are loaded simultaneously using mixture-of-experts routing:

```yaml
lora_moe_config:
  adapters: ["LORA-CODE-PYTHON-V3", "LORA-CODE-JS-V2", "LORA-DOCS-V1"]
  routing_strategy: "softmax_routing"  # or "top_k" with k=1

  routing_logic: |
    # Determine which adapter(s) to activate based on request routing
    router_weights = softmax(router_model.classify(request))
    active_adapters = top_k(zip(adapters, router_weights), k=1)
    output = Σ weight_i × adapter_i.forward(x)

  constraint: |
    All adapters in composition must have identical:
    - base_model.model_id
    - lora_config.rank
    - lora_config.target_modules
```

### Rule 3: Sequential Adapter Chaining

Not supported. If sequential application is needed, fine-tune a merged adapter instead.

---

## Adapter Serving Configuration

```yaml
serving_config:
  adapter_id: "LORA-CODE-PYTHON-V3-20260507"

  loading:
    load_strategy: "hot_swap"  # hot_swap | cold_load | preloaded
    # hot_swap: adapter loaded on first request, cached thereafter
    # preloaded: adapter loaded at service startup

    adapter_cache_size_mb: 128  # Memory footprint of adapter weights
    cache_eviction_policy: "LRU"
    max_cached_adapters: 10  # Per inference replica

  activation:
    merge_at_load: false  # True: merge into base model (faster inference, no swap)
    # False: apply adapter dynamically (enables hot-swapping between adapters)
    quantize_adapter: false  # May reduce quality; not recommended

  routing_trigger:
    # Automatically activate this adapter when:
    task_type_match: ["code_generation_simple", "code_generation_complex"]
    language_detected: "python"
    # Both conditions must be true
```

---

## Deprecation Protocol

```
STEP 1: Identify deprecation trigger
  - Successor adapter version available with superior benchmarks
  - Base model being retired
  - Quality regression detected in production

STEP 2: Set deprecation date (minimum 30-day notice)
  registry.update(adapter_id, {
    "lifecycle.status": "DEPRECATED",
    "lifecycle.deprecation_date": today + 30_days,
    "lifecycle.successor_adapter_id": successor_id
  })

STEP 3: Migrate traffic to successor adapter
  Route new requests to successor adapter during deprecation period.
  Monitor for regressions.

STEP 4: Retire adapter (on deprecation_date)
  registry.update(adapter_id, {
    "lifecycle.status": "RETIRED",
    "lifecycle.retirement_date": today
  })
  # Retired adapters remain in registry but cannot be served.
  # Weights archived for 90 days then deleted.
```