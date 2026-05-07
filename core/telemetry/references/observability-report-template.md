# Observability Report Template

## Weekly Observability Report

```
OBSERVABILITY REPORT — Week of YYYY-MM-DD
==========================================

PLATFORM HEALTH SUMMARY
  Overall health:   HEALTHY | DEGRADED | CRITICAL
  SLO status:       N/N SLOs within budget | N SLOs breached

SERVICE STATUS
  Service                  | Availability | P95 Latency | Error Rate | SLO Status
  -------------------------|-------------|-------------|------------|----------
  account-api              | 99.95%      | 245ms       | 0.02%      | OK
  inference-service        | 99.80%      | 1,245ms     | 0.15%      | AT RISK
  ...

ERROR BUDGET STATUS
  Service              | SLO Target | Budget Used (30d) | Status
  ---------------------|-----------|-------------------|--------
  account-api          | 99.9%     | 12% (5.2 min)     | OK
  inference-service    | 99.5%     | 67% (22 min)      | WARN
  ...

ALERT SUMMARY
  Total alerts fired:      N
  Pages (P0/P1):           N
  Tickets (P2):            N
  Inform (P3):             N
  False positives:         N
  Alert-to-incident ratio: X%

INCIDENTS
  INC-ID   | Severity | Duration | Root Cause Summary
  ---------|----------|----------|-------------------
  INC-001  | P1       | 1h 22m   | DB connection pool exhausted
  ...

TOP LATENCY DEGRADATIONS (vs previous week)
  1. [endpoint]: P95 increased from Xms to Xms (+Y%)
  2. ...

TOP ERROR RATE INCREASES
  1. [endpoint]: error rate increased from X% to X% (+Xpp)
  2. ...

MODEL INFERENCE METRICS
  Total requests:          N
  Avg latency:             Xms
  Cache hit rate:          X%
  Cloud overflow ratio:    X%
  Total cost:              $X

NEXT WEEK FOCUS
  1. [Action item — owner — target]
  2. [Action item — owner — target]
```

---

## SLO Burn Rate Dashboard

For each SLO, report the burn rate trend:

```
SLO: account-api availability (99.9%, 30d window)
  Error budget:          43.2 minutes
  Used (last 30d):       5.2 minutes (12%)
  Burn rate (last 1h):   0.3× (OK — below 1× baseline)
  Burn rate (last 6h):   0.8× (OK)
  Burn rate (last 24h):  0.5× (OK)
  Trend:                 Improving
  Projection:            Will exhaust 2% of budget by end of period
```

---

## Four Golden Signals Summary

Reported weekly at service level:

| Signal | What We Report | Source |
|---|---|---|
| Latency | P50, P95, P99 per endpoint | Histogram metrics |
| Traffic | Total requests, RPS trend | Counter metrics |
| Errors | 5xx rate, specific error types | Counter metrics |
| Saturation | CPU%, memory%, GPU%, queue depth | Gauge metrics |

---

## Metric Freshness

All metrics in this report are from the past 7 days unless noted.
Metrics with freshness > 24 hours are flagged as `[STALE]`.

Data sources:
- Service metrics: Prometheus / Grafana
- AI inference: runtime-economics telemetry events
- Incident data: sre-incident-response logs
- Alert data: alertmanager