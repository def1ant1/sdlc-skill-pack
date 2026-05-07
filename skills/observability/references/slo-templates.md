# SLO Templates

## SLO Definition Format

```yaml
slo:
  id: "SLO-<service>-<metric>"
  service: "<service name>"
  tier: "user-facing-revenue | user-facing-nonrevenue | internal-api | background-worker | batch-job"
  sli:
    name: "<SLI name>"
    type: "availability | latency | error_rate | throughput | completion"
    measurement: "<query or description>"
    data_source: "<metrics backend>"
  slo_target: 99.9           # percentage
  window: "30d"              # rolling window
  error_budget: 0.1          # derived: 100 - slo_target
  error_budget_consumed_alert: 50  # alert when 50% of budget consumed
  owner: "<team>"
  review_cadence: "quarterly"
```

---

## Standard SLO Targets by Tier

| Tier | Availability | Latency (P95) | Error Rate |
|---|---|---|---|
| User-facing (revenue path) | 99.9% (8.7h/year) | ≤ 500ms | ≤ 0.1% |
| User-facing (non-revenue) | 99.5% (43.8h/year) | ≤ 1,000ms | ≤ 0.5% |
| Internal API | 99.0% (87.6h/year) | ≤ 200ms | ≤ 1.0% |
| Background worker | 99.0% | N/A | ≤ 1.0% |
| Batch job | 95.0% | Completion within defined window | ≤ 5.0% |

---

## Error Budget Calculation

```
error_budget_minutes = (1 - slo_target/100) × window_minutes

For 99.9% SLO over 30 days:
  window_minutes = 30 × 24 × 60 = 43,200 min
  error_budget   = 0.001 × 43,200 = 43.2 min
```

Error budget consumption rate:
```
consumed_rate = (actual_downtime / error_budget) × 100%
```

---

## Burn Rate Alerts

Multi-window burn rate alerting prevents alert fatigue while catching both fast
and slow burns:

| Alert | Burn Rate | Window | Error Budget Consumed | Severity |
|---|---|---|---|---|
| Critical — fast burn | > 14× | 1h | 2% in 1h | Page immediately |
| Critical — slow burn | > 6× | 6h | 5% in 6h | Page |
| Warning — moderate burn | > 3× | 1d (day) | 10% in 1d | Ticket |
| Info — slow burn | > 1× | 3d | Any sustained | Inform |

```
burn_rate = error_rate / (1 - slo_target/100)

A burn rate of 1 means you'll exhaust your budget exactly at the end of the window.
A burn rate of 14 means you'll exhaust it in 1/14 of the window (≈ 2 days for 30d).
```

---

## SLO Templates by Service Type

### REST API (User-Facing Revenue)

```yaml
slos:
  - id: "SLO-api-availability"
    sli:
      type: availability
      measurement: "sum(rate(http_requests_total{status!~'5..'}[5m])) / sum(rate(http_requests_total[5m]))"
    slo_target: 99.9
    window: 30d

  - id: "SLO-api-latency-p95"
    sli:
      type: latency
      measurement: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
    slo_target: 99.0      # 99% of requests under 500ms
    threshold_ms: 500
    window: 30d
```

### Background Worker

```yaml
slos:
  - id: "SLO-worker-success-rate"
    sli:
      type: throughput
      measurement: "rate(jobs_completed_total[5m]) / rate(jobs_attempted_total[5m])"
    slo_target: 99.0
    window: 7d

  - id: "SLO-worker-lag"
    sli:
      type: latency
      measurement: "kafka_consumer_lag_sum"
    threshold: 1000        # max lag in messages
    slo_target: 95.0
    window: 7d
```

### Batch Job

```yaml
slos:
  - id: "SLO-batch-completion"
    sli:
      type: completion
      measurement: "batch_job_completed_within_window"
    slo_target: 95.0
    window_hours: 4        # must complete within 4h of scheduled start
    window: 30d
```

---

## SLO Review Process

**Quarterly review**:
1. Pull 90-day error budget consumption rate
2. If consumption < 10%: consider tightening SLO target
3. If consumption > 80%: review reliability investments; loosen SLO if justified
4. Update SLO document; notify stakeholders of changes
5. Changes to user-facing SLOs require Level-2 approval