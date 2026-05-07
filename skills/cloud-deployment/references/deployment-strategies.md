# Deployment Strategies

Used by `skills/cloud-deployment/SKILL.md` to select the right deployment strategy
based on change risk, platform, and rollback requirements.

---

## Strategy Selection Rules

Apply these rules in order. Use the first matching strategy.

| Rule | Strategy |
|---|---|
| Breaking change to database schema | Recreate (after migration; accept downtime) or Blue/Green with migration step |
| Zero-downtime required AND instant rollback required | Blue/Green |
| High-risk change, uncertain impact | Canary (start at 5% traffic) |
| Standard feature release, low risk | Rolling |
| Feature controlled by a flag | Feature flag (deploy anytime; release separately) |
| Stateless function/worker update | Recreate or Rolling (functions are stateless) |
| Edge/CDN deployment (Cloudflare Workers) | Rolling (near-instant global propagation) |

---

## Rolling Deployment

**How it works:** Replace instances one at a time. New version gradually takes over
while old version handles remaining traffic.

**Configuration:**
- `maxSurge`: 1 extra pod/instance during rollout
- `maxUnavailable`: 0 (no capacity reduction during rollout)
- Rollout rate: 25% → 50% → 75% → 100% (with health check at each step)

**Health check gate:** Confirm health check passes at each step before continuing.

**Rollback:** Halt rollout; reverse instance replacement (automated).

**Best for:** Standard releases, microservices, stateless applications.

---

## Blue/Green Deployment

**How it works:** Provision a complete new environment (green). Run health checks against
green. Cut traffic over from blue to green in a single atomic switch. Blue stays alive
for instant rollback.

**Steps:**
1. Deploy new version to green environment
2. Run full health check suite against green (not yet receiving production traffic)
3. Switch load balancer / DNS / Cloudflare routing rule to green
4. Monitor error rates and latency for 15 minutes
5. Decommission blue (or keep for 24h for safety)

**Rollback:** Switch load balancer back to blue (< 30 seconds).

**Best for:** High-traffic services, database-heavy apps, APIs with strict SLAs.

---

## Canary Deployment

**How it works:** Route a small percentage of traffic (5–10%) to the new version.
Monitor metrics. Gradually increase percentage if healthy. Roll back if metrics degrade.

**Traffic split progression:**
- Stage 1: 5% canary → monitor for 30 minutes
- Stage 2: 25% canary → monitor for 30 minutes
- Stage 3: 50% canary → monitor for 15 minutes
- Stage 4: 100% canary → full promotion

**Canary abort trigger:**
- Error rate > 2× baseline
- P95 latency > 1.5× baseline
- Any critical error in canary logs

**Best for:** High-risk changes, AI model upgrades, pricing changes.

---

## Feature Flag Deployment

**How it works:** Deploy code with new feature disabled. Enable for specific users,
segments, or percentage via a feature flag system.

**Advantages:**
- Decouple deployment from release
- Roll back without redeployment (just disable the flag)
- Gradual exposure to user segments

**Flag types:**
- Boolean on/off (for internal testing)
- Percentage rollout (0% → 10% → 50% → 100%)
- User segment targeting (beta users, enterprise accounts)

**Best for:** New features with user-visible changes, A/B experiments, gradual exposure.

---

## Canary Monitoring Checklist

```
[ ] Error rate: stable (< 2× baseline)
[ ] P95 latency: stable (< 1.5× baseline)
[ ] Business metrics: no anomaly (conversion, revenue)
[ ] Log scanning: no critical errors in canary instances
[ ] Database query time: no significant increase
[ ] Memory/CPU: within normal range for new pods
```

If any check fails at any stage: abort canary and rollback.