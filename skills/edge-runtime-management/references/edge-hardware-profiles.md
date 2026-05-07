# Edge Runtime Management — Hardware Profiles & Model Selection Matrix

## Edge Hardware Profiles

| Profile ID | Representative Hardware | CPU | RAM | Accelerator | Storage | Use Case |
|-----------|------------------------|-----|-----|-------------|---------|----------|
| `EDGE-NANO` | Raspberry Pi 5 | ARM Cortex-A76 4-core | 8GB | None | 500GB SSD | Sensor gateway, basic classification |
| `EDGE-MICRO` | Intel NUC (i5/i7) | x86_64 4–8 core | 16–32GB | Intel iGPU | 1TB SSD | Light inference, document processing |
| `EDGE-STANDARD` | NVIDIA Jetson Orin NX | ARM A78AE 8-core | 16GB | NVIDIA 1024-core Ampere GPU | 1TB NVMe | On-device inference, vision AI |
| `EDGE-ADVANCED` | NVIDIA Jetson AGX Orin | ARM A78AE 12-core | 64GB | NVIDIA 2048-core Ampere GPU | 2TB NVMe | Multi-modal inference, complex tasks |
| `EDGE-SERVER` | Workstation with RTX 4090 | x86_64 16-core | 64GB | NVIDIA RTX 4090 24GB | 4TB NVMe | High-capability edge server |

---

## Model Selection Matrix

| Hardware Profile | Recommended Model | Engine | Format | Parameter Count | VRAM Req |
|-----------------|-----------------|--------|--------|----------------|----------|
| `EDGE-NANO` | llama-3.2-1b-instruct | llama.cpp | GGUF Q4_K_M | 1B | 0 (CPU only) |
| `EDGE-MICRO` | llama-3.2-3b-instruct | llama.cpp | GGUF Q4_K_M | 3B | 0 (CPU only) |
| `EDGE-STANDARD` | llama-3.2-3b-instruct | Ollama | GGUF Q8_0 | 3B | 4GB |
| `EDGE-ADVANCED` | llama-3.1-8b-instruct | Ollama | GGUF Q8_0 | 8B | 10GB |
| `EDGE-SERVER` | llama-3.1-13b-instruct | vLLM | BF16 | 13B | 22GB |

---

## Model Selection Algorithm

```python
def select_edge_model(hardware_profile: str, task_requirements: dict) -> EdgeModelConfig:
    """
    Select the optimal model for an edge node based on hardware and task requirements.
    """
    PROFILE_SPECS = {
        "EDGE-NANO":     {"cpu_only": True, "max_ram_gb": 8,  "gpu_vram_gb": 0},
        "EDGE-MICRO":    {"cpu_only": True, "max_ram_gb": 32, "gpu_vram_gb": 0},
        "EDGE-STANDARD": {"cpu_only": False, "max_ram_gb": 16, "gpu_vram_gb": 8},
        "EDGE-ADVANCED": {"cpu_only": False, "max_ram_gb": 64, "gpu_vram_gb": 16},
        "EDGE-SERVER":   {"cpu_only": False, "max_ram_gb": 64, "gpu_vram_gb": 24},
    }

    spec = PROFILE_SPECS[hardware_profile]

    # Filter candidate models by hardware constraint
    candidates = [
        m for m in MODEL_CATALOG
        if (m.vram_required_gb <= spec["gpu_vram_gb"] or spec["cpu_only"] and m.cpu_compatible)
        and m.ram_required_gb <= spec["max_ram_gb"] * 0.7  # Leave 30% headroom
    ]

    # Select highest quality model that meets task_requirements
    task_complexity = task_requirements.get("complexity", "standard")
    if task_complexity == "complex":
        # Prefer larger models
        candidates.sort(key=lambda m: m.parameter_count, reverse=True)
    else:
        # Prefer fastest (lowest latency) models
        candidates.sort(key=lambda m: m.estimated_tps, reverse=True)

    return candidates[0] if candidates else None
```

---

## OTA Update Protocol

```yaml
ota_update:
  update_id: "OTA-2026-xxxxx"
  update_type: model | firmware | config

  # Scheduling
  schedule:
    window_start: "02:00"              # Local time at edge node
    window_end: "04:00"
    days: [sunday]                     # Weekly maintenance window

  # Staged rollout
  rollout:
    pilot_group_pct: 5                 # Deploy to 5% first
    pilot_validation_hours: 24         # Observe for 24 hours
    rollout_phases: [5, 25, 50, 100]  # Progressive rollout percentages

  # Rollback policy
  rollback:
    trigger: "health_check_failure OR error_rate > 0.05"
    max_rollback_time_minutes: 5
    keep_previous_versions: 2

  # Validation after OTA
  post_update_validation:
    - health_check: true
    - inference_test:
        prompt: "What is 2 + 2?"
        expected_contains: "4"
        max_latency_ms: 5000
    - resource_check:
        max_memory_usage_pct: 85
```

---

## Disconnected Operation Specification

```yaml
disconnected_operation:
  detection:
    check_interval_seconds: 30
    connectivity_timeout_seconds: 10
    declare_disconnected_after_failures: 3

  local_serving:
    enabled: true
    # Continue serving inference from local model
    model_already_loaded: true
    # No new model downloads while disconnected

  telemetry_buffering:
    enabled: true
    buffer_location: "/var/edge-os/telemetry-buffer"
    max_buffer_size_mb: 500
    overflow_policy: drop_oldest

  observation_buffering:
    enabled: true
    tag_as: "offline_collected"
    max_observations: 10000

  reconnection:
    sync_priority:
      - pending_escalations    # First: any escalations generated while offline
      - observation_buffer     # Second: buffered world-model observations
      - telemetry_buffer       # Third: telemetry data
    conflict_resolution: "server_wins"  # Server state takes precedence on reconnect
    notify_on_reconnect: true
```