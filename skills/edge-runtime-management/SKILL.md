---
name: edge-runtime-management
description: Manages edge node deployment, tiny model selection, disconnected operation, and OTA firmware and model updates for sovereign edge AI deployments.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['inference-engine-fleet', 'cluster-management']

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

Sovereign edge AI runtime manager. Extends the Enterprise OS inference capability to
resource-constrained edge nodes operating in low-connectivity or air-gapped environments.
Manages edge node fleet registration, model selection for edge constraints, disconnected
operation protocols, and over-the-air updates.

## Activation Triggers

- A new edge node is commissioned and requires initial provisioning
- A model or firmware update is published and requires OTA deployment to the edge fleet
- An edge node's connectivity status changes (disconnected/reconnected)
- An edge node's resource utilization exceeds its capacity (rightsizing trigger)
- `iot-data-ingestion` detects a new IoT source that requires edge inference
- A scheduled edge fleet health check is due

## Execution Protocol

1. **Edge node registry**: Maintain a registry of all edge nodes with:
   - Hardware profile (CPU, RAM, GPU/NPU if present, storage)
   - Current firmware version, model version, connectivity status
   - Last heartbeat timestamp

2. **Model selection for edge**: Given an edge node's hardware profile, recommend the
   optimal quantized model:
   - CPU-only, < 4GB RAM: llama.cpp GGUF Q4_K_M or Q2_K (≤ 3B parameter models)
   - CPU + NPU: optimized INT8 model for the specific NPU architecture
   - Edge GPU (RTX 4090 class): GGUF Q8 or FP16 models up to 13B parameters

3. **OTA update orchestration**: For model or firmware updates:
   - Stage update to edge CDN
   - Schedule download during off-peak hours (low-traffic window)
   - Apply update with rollback: if new version fails health check, revert to previous
   - Confirm update completion and update registry

4. **Disconnected operation**: During connectivity loss:
   - Edge node serves requests from locally loaded model (no cloud dependency)
   - Buffer telemetry and observations locally
   - On reconnect: sync buffered data to `world-model` and `telemetry`
   - Flag any observations collected during disconnection as `offline_collected`

5. **Fleet health monitoring**: Aggregate edge node health metrics.
   Alert when > 5% of fleet is unreachable for > 30 minutes.

## Output Format

```yaml
edge_fleet:
  total_nodes: 0
  online: 0
  offline: 0
  pending_updates: 0
  node_status:
    - node_id: "edge-node-001"
      status: online | offline | updating
      model: "llama-3-2-3b-q4"
      firmware: "edge-os-2.1.0"
      last_heartbeat: "2026-05-07T10:00:00Z"
```

## Quality Gates

- OTA updates must be validated on a staging node before fleet-wide rollout
- Disconnected operation must be verified for each node type during initial commissioning

## References

- `references/` — Edge hardware profiles, model selection matrix, OTA update protocol, disconnected operation spec
