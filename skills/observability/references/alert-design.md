# Alert Design

## Alert Design Principles

1. **Alert on symptoms, not causes**: Page on-call when users are impacted, not when a CPU spikes.
2. **Every alert must be actionable**: If the on-call cannot take a specific action, the alert should not exist.
3. **Every alert must have a runbook**: No orphan alerts. Runbook link is required.
4. **Alerts must have the right severity**: Under-severity wastes incident budget; over-severity causes fatigue.
5. **Minimize noise**: An alert that fires daily for non-incidents trains engineers to ignore it.

---

## Severity Levels

| Severity | Meaning | Response | Notification |
|---|---|---|---|
| Page (P0/P1) | User-impacting right now; needs immediate action | Wake someone up; 5-min response | PagerDuty → on-call engineer → escalation |
| Ticket (P1/P2) | Important; fix within hours/day; not user-impacting yet | Create incident ticket; respond in business hours | Slack alert channel + ticket |
| Inform (P3) | Trending toward a problem; fix this sprint | Awareness only | Slack monitoring channel |

---

## Alert Record Format

```yaml
alert:
  name: "HighErrorRate-AccountService"
  severity: page | ticket | inform
  summary: "<one sentence: what is wrong>"
  description: "<more context: what metric, what threshold, what impact>"
  runbook: "https://runbooks.apotheon.ai/account-service/high-error-rate"
  service: "account-service"
  team: "platform"
  slo: "SLO-api-availability"     # link to the SLO this alert protects
  labels:
    env: production
    component: api
  expr: |
    sum(rate(http_requests_total{service="account-service",status=~"5.."}[5m]))
    / sum(rate(http_requests_total{service="account-service"}[5m])) > 0.01
  for: 5m                          # must be true for this duration before firing
  inhibit_when:                    # suppress if these alerts are also firing
    - "ServiceDown-AccountService"
```

---

## Alert Quality Gates

Before adding a new alert, verify:

- [ ] Alert fires on a user-observable symptom (not internal metric)
- [ ] Threshold validated against 30 days of historical data (avoid alert on normal variance)
- [ ] `for` duration prevents flapping (≥ 2 minutes for most; ≥ 5 minutes for noisy metrics)
- [ ] Runbook exists and is up to date
- [ ] Alert has been tested: can you reproduce the condition in staging?
- [ ] Inhibition rules configured to prevent duplicate alerts for the same root cause
- [ ] Alert ownership assigned to a team (no orphan alerts)

---

## Runbook Template

```markdown
# Runbook: <Alert Name>

## Alert Summary
<One-paragraph description of what this alert means>

## Severity: <Page | Ticket | Inform>

## Initial Triage (first 5 minutes)
1. Check <link to dashboard> — what is the current error rate?
2. Check recent deploys: `kubectl rollout history deployment/account-service`
3. Check dependencies: <link to dependency health dashboard>

## Diagnosis Steps
- If error rate > 10%: likely a code regression → proceed to rollback
- If error rate 1–10%: likely a dependency issue → check downstream services
- If no recent deploy: check infra events (scaling events, network changes)

## Mitigation Options
1. Rollback: `kubectl rollout undo deployment/account-service`
2. Circuit break: enable `FEATURE_CIRCUIT_BREAK=true` feature flag
3. Scale up: `kubectl scale deployment/account-service --replicas=N`

## Escalation
- If not resolved in 30 min: escalate to <on-call manager>
- If data loss suspected: escalate to <VP Engineering> immediately

## Links
- Dashboard: <link>
- Logs: <link>
- Recent incidents: <link>
```

---

## Noise Reduction Rules

| Problem | Solution |
|---|---|
| Alert flaps (fires and resolves repeatedly) | Increase `for` duration; add hysteresis |
| Too many alerts for one root cause | Add inhibition rules; fire only the highest-level alert |
| Alert fires in maintenance window | Add maintenance window silence in alertmanager |
| Alert fires only in off-peak (low traffic, different baseline) | Use relative thresholds (burn rate) not absolute |
| Alert fires for synthetic/test traffic | Filter test traffic in metric labels |

---

## Alert Lifecycle

**Review cadence**: All active alerts reviewed quarterly.

- Any alert that fires > 5 times per week with 0 pages opened: review threshold or retire
- Any alert that has never fired in 6 months: review relevance or retire
- Any alert without a runbook link: block in CI (automated check)