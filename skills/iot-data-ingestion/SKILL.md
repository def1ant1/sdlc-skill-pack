---
name: iot-data-ingestion
description: Supports MQTT/CoAP/OPC-UA protocols for sensor data processing, normalization, and edge-to-cloud synchronization via the enterprise data fabric.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['data-fabric', 'event-bus']

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

IoT protocol gateway and data normalization layer. Ingests real-time sensor and device
data from industrial and enterprise IoT deployments via MQTT, CoAP, and OPC-UA protocols.
Normalizes heterogeneous sensor data to the platform's canonical time-series schema,
applies edge filtering to reduce unnecessary cloud transmission, and synchronizes
processed data to `data-fabric` for downstream analytics and AI inference.

## Activation Triggers

- An MQTT message arrives on a subscribed topic
- A CoAP observation notification is received from a registered endpoint
- An OPC-UA subscription publishes a monitored item value change
- A bulk data sync from an edge node reconnecting after disconnected operation
- An operator registers a new IoT data source
- Sensor data quality drops below the noise floor threshold (data quality alert)

## Execution Protocol

1. **Protocol handling**:
   - MQTT: subscribe to configured topics; handle QoS 0, 1, 2
   - CoAP: register observation on configured CoAP servers; handle confirmable messages
   - OPC-UA: create subscriptions on OPC-UA server nodes; handle data change callbacks

2. **Data normalization**: Transform raw protocol payloads to the canonical IoT reading schema:
   ```yaml
   iot_reading:
     source_id: "sensor/factory-floor/temperature-007"
     timestamp: "2026-05-07T10:00:00.000Z"
     metric: temperature
     value: 72.4
     unit: fahrenheit
     quality: good | uncertain | bad
   ```

3. **Edge filtering**: Apply configurable filters before cloud transmission:
   - Dead-band filtering: suppress readings within ±N% of the previous transmitted value
   - Aggregation: for high-frequency sensors, aggregate to 1-second or 1-minute summaries
   - Anomaly pass-through: always transmit readings outside ±3σ of recent baseline regardless of dead-band

4. **Data fabric ingestion**: Batch filtered readings and write to `data-fabric` time-series store.
   Apply schema governance labels (data classification, source system, retention policy).

5. **Event emission**: For anomalous readings (outside expected range), emit a real-time
   alert on `event-bus` for downstream agents and skills.

## Output Format

```yaml
iot_ingestion:
  source_id: "sensor/factory-floor/temperature-007"
  readings_received: 0
  readings_transmitted: 0
  readings_filtered: 0
  anomalies_detected: 0
  ingest_latency_ms: 0
  data_fabric_write_status: success | buffered | failed
```

## Quality Gates

- End-to-end latency from sensor to `data-fabric`: < 5 seconds for QoS 1+ data
- Bad quality readings must be flagged, not silently discarded

## References

- `references/` — Protocol configuration spec, canonical IoT reading schema, dead-band filter parameters
