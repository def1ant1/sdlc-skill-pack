# Blameless Post-Mortem Template

## Document Header

```
POST-MORTEM REPORT
==================
Incident:     INC-YYYY-NNN
Title:        <one-sentence incident description>
Severity:     P0 | P1 | P2
Date:         YYYY-MM-DD
Author:       <author name>
Reviewers:    <names>
Published:    YYYY-MM-DD
Status:       Draft | In Review | Final
```

---

## Blameless Principle

This post-mortem is a learning document, not a blame document. Incidents are
caused by systemic factors — unclear processes, insufficient tooling, inadequate
testing, missing safeguards — not by individual mistakes. The goal is to improve
the system so the same failure cannot happen the same way again.

**Do not name individuals as root causes.** Name processes, systems, and gaps.

---

## Section 1 — Executive Summary

One paragraph. Describe what happened, how long it lasted, who was affected,
and what the primary contributing factor was. Written for a non-technical audience.

```
On YYYY-MM-DD at HH:MM UTC, <service> became unavailable for <duration>, affecting
approximately <N> users. The incident was caused by <primary cause>. The issue was
mitigated by <mitigation action> and fully resolved at HH:MM UTC. Total revenue
impact is estimated at $X.
```

---

## Section 2 — Impact

| Metric | Value |
|---|---|
| Duration | Xh Ym (HH:MM UTC – HH:MM UTC) |
| Users affected | ~N (X% of total active users) |
| Requests affected | ~N (X% failure rate) |
| Revenue impact | ~$X (estimated) |
| SLA impact | X minutes of error budget consumed |
| Regions affected | <list> |

---

## Section 3 — Timeline

```
[HH:MM UTC] DETECTED: <what was detected and by whom>
[HH:MM UTC] DECLARED: P<severity> — <title>
[HH:MM UTC] IC ASSIGNED: <role, not name>
[HH:MM UTC] DIAGNOSED: <first hypothesis formed>
[HH:MM UTC] ACTION: <action taken> → <outcome>
[HH:MM UTC] ACTION: <action taken> → <outcome>
[HH:MM UTC] MITIGATED: <what reduced user impact>
[HH:MM UTC] RESOLVED: <what fully restored service>
[HH:MM UTC] POST-MORTEM INITIATED
```

---

## Section 4 — Root Cause Analysis

### Primary Root Cause

One clear sentence. The single factor that, if absent, would have prevented this incident.

```
The deployment pipeline did not validate that the new configuration value was
within the accepted range before applying it to production.
```

### Contributing Factors

List all systemic factors that made the incident possible or worse:

1. **No pre-flight validation**: The configuration schema was not validated at deploy time, allowing an invalid value to propagate to production.
2. **Alert gap**: The metric that spiked was not in the SLO alert set; detection came from user reports 15 minutes after impact began.
3. **Runbook outdated**: The runbook for this service did not include the configuration rollback procedure, slowing mitigation by 20 minutes.

---

## Section 5 — What Went Well

Recognize what worked during the incident response:

- [ ] On-call response time was within SLA (acknowledged in < 5 min)
- [ ] Rollback was executed cleanly and restored service
- [ ] Communication cadence was maintained (update every 30 min)
- [ ] Cross-team coordination was effective

---

## Section 6 — What Could Have Gone Better

Be specific; these feed directly into action items:

- Detection took 15 minutes longer than it should have because the alert was not configured
- Runbook did not cover the actual failure scenario encountered
- DB connection pool had no monitoring; exhaustion was not caught until service degraded

---

## Section 7 — Action Items

Every action item must have: owner (role/team, not individual), due date, and priority.

| ID | Action | Type | Owner | Priority | Due Date | Status |
|---|---|---|---|---|---|---|
| AI-001 | Add config range validation to deploy pipeline | Prevention | Platform team | P0 | YYYY-MM-DD | Open |
| AI-002 | Add alert for DB connection pool utilization > 80% | Detection | SRE | P1 | YYYY-MM-DD | Open |
| AI-003 | Update runbook with configuration rollback steps | Mitigation | Service team | P1 | YYYY-MM-DD | Open |
| AI-004 | Add config validation to pre-deploy smoke test | Prevention | QA | P2 | YYYY-MM-DD | Open |

Action types: `Prevention` (stop recurrence) | `Detection` (catch faster) | `Mitigation` (reduce impact) | `Process` (improve response)

---

## Section 8 — Lessons Learned

2–4 sentences synthesizing the systemic lessons from this incident for the engineering organization.

---

## Review and Distribution

- Draft due: within 24h of resolution (P0) / 48h (P1)
- Review by: IC, on-call engineer, and Engineering Manager
- Final published to: #post-mortems channel and internal wiki
- Action items tracked in: workflow-engine with due date alerts