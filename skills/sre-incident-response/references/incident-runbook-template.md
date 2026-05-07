# Incident Runbook Template

## Runbook Header

```
INCIDENT RUNBOOK
================
Service:      <service name>
Runbook-ID:   RB-<service>-<scenario>
Last updated: YYYY-MM-DD
Owner:        <team>
Triggered by: <alert name>
```

---

## Section 1 — Severity Classification

Use the following criteria to assign severity immediately on detection:

| Severity | Criteria | Examples |
|---|---|---|
| P0 | Full service outage; data loss; security breach; revenue-critical path down | Checkout unavailable; database corruption; credential leak |
| P1 | Major feature broken; > 20% users impacted; performance severely degraded | API error rate > 10%; login broken for subset of users |
| P2 | Partial degradation; < 20% users impacted; workaround available | Slow search; one non-critical feature returning errors |
| P3 | Minor issue; no user impact; cosmetic | Incorrect display text; minor UI glitch |

**When in doubt: assign higher severity and downgrade if evidence warrants.**

---

## Section 2 — Escalation Matrix

| Severity | On-Call | Manager | VP Engineering | CEO |
|---|---|---|---|---|
| P0 | Page immediately | Notify immediately | Notify immediately | Notify if > 30 min |
| P1 | Page | Notify | Notify if > 2h | — |
| P2 | Slack | Business hours | — | — |
| P3 | Ticket | — | — | — |

---

## Section 3 — Initial Triage (First 5 Minutes)

Incident commander runs these checks immediately:

1. **Confirm the incident** — is the alert a real user-impacting event or a false positive?
   - Check real user traffic patterns, not just the metric that fired
   - If false positive: cancel incident, tune alert, document

2. **Assess scope**:
   - What percentage of users/requests are affected?
   - Which services are affected (direct and downstream)?
   - Is this isolated to one region/zone?

3. **Identify recent changes**:
   - What deployed in the last 24 hours?
   - Any config changes, feature flag changes, or infrastructure changes?
   - Any upstream dependency incidents?

4. **Declare severity** based on scope assessment.

---

## Section 4 — Scenario-Specific Runbooks

### Scenario: High Error Rate (5xx)

```
1. Check recent deployments → if any in last 2h: rollback first, diagnose after
2. Check application logs for error patterns:
   - log_query: level=error service=<service> | last 15min
3. Check upstream dependencies (DB, cache, external APIs):
   - DB: connection pool exhausted? queries timing out?
   - Cache: miss rate spike? eviction rate spike?
4. Check resource saturation: CPU > 90%? Memory > 85%?
5. Mitigation options:
   A. Rollback last deploy (fastest if deploy-related)
   B. Scale replicas (if capacity-related)
   C. Enable circuit breaker for affected dependency
   D. Restart pods (last resort — masks root cause)
```

### Scenario: High Latency

```
1. Check P50 vs P99 — is this a hot spot (few slow requests) or broad slowness?
2. Identify slow requests: use distributed traces to find bottleneck
3. Common causes:
   - Database: slow query, missing index, lock contention
   - External API: dependency latency spike
   - Memory pressure: GC pauses, high allocation rate
   - Queue backup: consumer lag
4. Mitigation:
   A. Kill slow queries if DB-related (WITH CAUTION — data safety first)
   B. Add caching layer if repeated expensive queries
   C. Increase replicas if CPU/memory pressure
   D. Shed load via rate limiting if overload
```

### Scenario: Service Down (0% availability)

```
1. Check pod/container health: are pods running?
2. Check DNS: is the service address resolving?
3. Check networking: load balancer health? security group rules changed?
4. Check recent infrastructure changes
5. Escalate to P0 immediately; notify VP Engineering
6. Mitigation:
   A. Restart deployment: kubectl rollout restart deployment/<name>
   B. If infrastructure: engage platform/infra team immediately
   C. If DNS: manual override to last known good endpoint
```

---

## Section 5 — Communication Templates

### P0 Initial Notification (send within 5 min of declaration)

```
🔴 P0 INCIDENT DECLARED — <service> <impact description>

INCIDENT: INC-YYYY-NNN
Time declared: HH:MM UTC
IC: <name>
Impact: <user impact description>
Status: Investigating

Next update: in 30 minutes or on status change.
Incident channel: #inc-<NNN>
```

### P0 Update (every 30 min)

```
🔴 P0 UPDATE — <service> — HH:MM UTC

Status: <Investigating | Mitigating | Near resolution>
Current impact: <description>
Actions taken: <list>
Next steps: <what IC is doing now>
Next update: in 30 minutes
```

### Resolution Notice

```
✅ RESOLVED — <service>

Incident: INC-YYYY-NNN
Duration: Xh Ym
Users affected: ~N
Impact: <description>
Resolution: <what was done>

Post-mortem will be published within 48h.
```

---

## Section 6 — Incident Closure

Before closing:
- [ ] Error rates returned to baseline for minimum 15 minutes
- [ ] All affected services showing healthy in dashboard
- [ ] Resolution notice sent to stakeholders
- [ ] Incident timeline complete in incident log
- [ ] Post-mortem initiated (assigned owner, due within 48h for P0/P1)