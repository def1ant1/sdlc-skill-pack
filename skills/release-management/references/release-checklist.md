# Release Checklist

## Pre-Release Gate (T-3 days)

### Code Readiness
- [ ] All planned features merged to release branch
- [ ] No open CRITICAL or HIGH severity bugs targeting this release
- [ ] All FAIL-level code review findings resolved
- [ ] Security scan: 0 CRITICAL, 0 HIGH unacknowledged findings
- [ ] Test coverage gates passing on release branch

### QA Sign-Off
- [ ] All acceptance criteria verified for P0 user stories
- [ ] Regression suite passing (≥ 99% pass rate)
- [ ] Performance test: P95 latency within SLO at target RPS
- [ ] Accessibility: Lighthouse score ≥ 90; no WCAG A/AA violations

### Documentation
- [ ] Changelog drafted and reviewed
- [ ] API changelog updated (breaking changes highlighted)
- [ ] User-facing docs updated for any changed behavior
- [ ] Internal runbooks updated for new operational requirements

---

## Release Day Checklist (T-0)

### Pre-Deployment (30 min before)
- [ ] On-call engineer confirmed on duty and briefed
- [ ] Rollback plan documented and tested (rollback takes < 10 min)
- [ ] Feature flags configured for canary rollout (if applicable)
- [ ] Database migration scripts reviewed and tested against prod schema snapshot
- [ ] Release communication drafted (customer-facing if applicable)

### Deployment (Production)
- [ ] Deployment triggered via CI/CD pipeline (not manual)
- [ ] Level-3 approval obtained (for production deployments — required per governance)
- [ ] Database migrations executed successfully
- [ ] Smoke tests passing on production within 10 min of deployment

### Post-Deployment Verification (0–60 min)
- [ ] Error rate at baseline (< 1% 5xx on all endpoints)
- [ ] Latency at baseline (P95 within SLO thresholds)
- [ ] Key business metrics not degraded (signups, conversions, API success rates)
- [ ] No anomalous alert fires in observability dashboard
- [ ] Feature-specific metrics instrumenting correctly

---

## Rollback Criteria

Trigger rollback immediately if ANY of the following:

| Signal | Threshold | Action |
|---|---|---|
| 5xx error rate | > 5% for 5 min post-deploy | Rollback |
| P95 latency | > 2× baseline for 5 min | Rollback |
| Core business metric | Drop > 20% vs pre-deploy baseline | Rollback |
| Data integrity error | Any | Rollback + escalate to P0 |
| Security alert | Any post-deploy security alert | Rollback + escalate to P0 |

**Rollback decision authority**: On-call engineer (no approval required for rollback).
Notify VP Engineering and release manager immediately on rollback.

---

## Post-Release (T+24h)

- [ ] Release retrospective completed (15 min async or sync)
- [ ] Any issues during deployment documented
- [ ] Rollback (if occurred) post-mortem initiated
- [ ] Changelog published to customers (if applicable)
- [ ] Release metrics captured: deployment duration, rollback rate, incident count

---

## Hotfix Release Checklist

For emergency fixes bypassing the normal cycle:

- [ ] P0 or P1 incident declared and documented
- [ ] Root cause identified and fix scoped to minimal change
- [ ] Expedited code review (minimum 1 reviewer + security review if applicable)
- [ ] Smoke tests run on staging
- [ ] Level-3 approval obtained (required even for hotfixes)
- [ ] All normal post-deployment checks apply
- [ ] Full regression suite run within 24h of hotfix deploy