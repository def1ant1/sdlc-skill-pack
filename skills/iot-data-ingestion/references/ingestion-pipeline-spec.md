# IoT Data Ingestion — Ingestion Pipeline Specification

## Supported IoT Protocols

| Protocol | Port | Use Case | TLS Required | Auth |
|----------|------|---------|-------------|------|
| MQTT 3.1.1 | 1883 (8883 TLS) | Sensor telemetry, low-bandwidth devices | Yes (mTLS preferred) | Client cert or username/token |
| MQTT 5.0 | 8883 | Modern IoT; session expiry, user properties | Yes | mTLS |
| AMQP 1.0 | 5671 | Enterprise IoT gateways | Yes | mTLS + SASL |
| HTTP/S REST | 443 | Batch ingest, high-payload devices | Yes | API key + JWT |
| WebSocket | 443 | Streaming from browser-connected devices | Yes | JWT |

---

## Device Registry Schema

```yaml
iot_device:
  device_id: "DEV-2026-xxxxx"
  device_type: sensor | gateway | actuator | camera | edge_node
  model: "Raspberry Pi 5 — Environmental Sensor"
  hardware_profile: EDGE-NANO   # Reference to edge-hardware-profiles.md

  location:
    site_id: "SITE-NYC-01"
    building: "HQ"
    floor: 3
    zone: "Server Room A"
    lat: 40.7128
    lon: -74.0060

  connectivity:
    protocol: mqtt5
    broker_endpoint: "mqtt.apotheon.io:8883"
    topic_prefix: "apotheon/devices/DEV-2026-xxxxx"
    client_cert_id: "CERT-DEV-2026-xxxxx"
    qos: 1     # 0 = at-most-once, 1 = at-least-once, 2 = exactly-once

  telemetry_schema:
    - field: temperature_c
      type: float
      unit: celsius
      range: [-40, 125]
      sample_rate_hz: 0.1    # One sample every 10 seconds
    - field: humidity_pct
      type: float
      unit: percent
      range: [0, 100]
      sample_rate_hz: 0.1
    - field: co2_ppm
      type: int
      unit: ppm
      range: [0, 5000]
      sample_rate_hz: 0.033  # One sample every 30 seconds

  firmware:
    version: "2.4.1"
    last_updated_at: "2026-04-01T00:00:00Z"
    ota_enabled: true

  status: online | offline | degraded | maintenance
  registered_at: "2026-01-15T10:00:00Z"
  last_seen_at: "2026-05-07T10:00:00Z"
```

---

## Telemetry Message Schema (MQTT Payload)

```json
{
  "device_id": "DEV-2026-xxxxx",
  "timestamp": "2026-05-07T10:00:00.000Z",
  "sequence_number": 14820,
  "readings": {
    "temperature_c": 22.4,
    "humidity_pct": 45.2,
    "co2_ppm": 412
  },
  "quality_flags": {
    "temperature_c": "good",
    "humidity_pct": "good",
    "co2_ppm": "good"
  },
  "firmware_version": "2.4.1",
  "battery_pct": 87
}
```

---

## Ingestion Pipeline Architecture

```
DEVICE → MQTT BROKER → INGESTION SERVICE → PROCESSING → STORAGE

Device sends telemetry (MQTT publish)
        │
        ▼
MQTT Broker (Eclipse Mosquitto / EMQX)
  ├── TLS termination
  ├── Client certificate validation
  └── Topic ACL enforcement
        │
        ▼
Ingestion Service (subscribes to apotheon/devices/#)
  ├── Message validation (schema check vs. device registry)
  ├── Deduplication (sequence_number based, 60s window)
  └── Quality flag assessment
        │
        ├── Quality: GOOD → route to TimeSeries DB
        ├── Quality: DEGRADED → route to TimeSeries DB + alert
        └── Quality: BAD → quarantine; alert device owner
        │
        ▼
Fan-out:
  ├── TimeSeries DB (InfluxDB / TimescaleDB): raw + downsampled
  ├── Event Bus (Kafka): for real-time consumers (alerting, ML)
  └── Cold Storage (GCS): compressed parquet, partitioned by date/device
```

---

## Data Quality Rules

```yaml
data_quality_rules:
  - rule: range_check
    description: "Reading within declared sensor range"
    action_on_fail: flag_bad

  - rule: rate_of_change
    description: "Delta between consecutive readings not physically impossible"
    threshold:
      temperature_c_per_second: 5.0   # >5°C/s = sensor error
    action_on_fail: flag_degraded

  - rule: missing_fields
    description: "All declared telemetry fields present"
    action_on_fail: flag_degraded

  - rule: heartbeat
    description: "Device has sent a message within 2× expected sample interval"
    action_on_fail: alert_offline

  - rule: sequence_gap
    description: "sequence_number monotonically increasing"
    action_on_fail: log_warning   # May indicate message loss
```

---

## Downsampling & Retention Policy

| Resolution | Retention | Storage | Notes |
|-----------|-----------|---------|-------|
| Raw (10s) | 7 days | InfluxDB hot tier | Exact readings |
| 1-minute mean | 90 days | InfluxDB warm tier | MEAN + MIN + MAX |
| 1-hour mean | 2 years | TimescaleDB | MEAN + MIN + MAX + STDDEV |
| 1-day summary | 10 years | GCS cold storage | Full statistical summary |

Downsampling runs as a scheduled Temporal workflow every hour.

---

## Alert Rules

```yaml
iot_alert_rules:
  - rule_id: "IOT-ALERT-001"
    name: "Device offline"
    condition: "no message received for > 2× sample_interval"
    severity: medium
    notify: [infrastructure-optimization-agent, sre-agent]

  - rule_id: "IOT-ALERT-002"
    name: "Sensor reading out of range"
    condition: "quality_flag == bad for > 3 consecutive readings"
    severity: high
    notify: [sre-agent]

  - rule_id: "IOT-ALERT-003"
    name: "Environmental threshold breach"
    condition: "temperature_c > 35 OR co2_ppm > 2000"
    severity: high
    notify: [facilities-team, sre-agent]
    action: create_itsm_incident
```