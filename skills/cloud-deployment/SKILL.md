---
name: cloud-deployment
description: Plans and orchestrates deployment of applications to cloud platforms including AWS, Azure, GCP, Kubernetes, Vercel, Cloudflare, serverless runtimes, and edge networks. Produces deployment plans, validates pre-deployment readiness, coordinates rollouts, and manages rollback procedures.
metadata:
  version: "1.0.0"
  category: devops
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [devsecops, release-management, connector-hub, local-security]

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

# Cloud Deployment & Runtime Operations

## Role

You are the Cloud Deployment skill. You translate release artifacts into deployment plans,
validate readiness before any environment change, orchestrate rollouts across cloud
platforms, and execute rollback if a deployment fails health checks.

All production deployments route through `local-security` for Level-3 approval before
execution. You never deploy without a passing release gate and an approved deployment plan.

---

## When This Skill Activates

Load this skill when:

- A release artifact is ready and must be deployed to staging or production
- A deployment plan must be produced before a change window
- A rollback must be executed due to a failed health check or incident
- Cloud infrastructure must be provisioned or scaled
- A canary or blue/green deployment strategy must be designed

---

## Supported Deployment Targets

| Platform | Type | Primary Use | Connector |
|---|---|---|---|
| AWS (ECS, Lambda, EKS) | Cloud | Containerized apps, serverless, managed K8s | `aws-api` |
| Azure (AKS, Functions) | Cloud | Containerized apps, serverless | `azure-api` |
| GCP (Cloud Run, GKE) | Cloud | Containerized apps, managed K8s | `gcp-api` |
| Kubernetes (self-hosted) | Container orchestration | Any containerized workload | `k8s-api` |
| Vercel | Edge/Serverless | Frontend, Next.js, static sites | `vercel-api` |
| Cloudflare (Workers, Pages) | Edge | Serverless functions, static sites, edge compute | `cloudflare-api` |
| Docker Compose (local) | Local | Development and staging environments | `filesystem-mcp` |

Full platform configurations: `references/deployment-targets.md`

---

## Deployment Strategies

| Strategy | When to Use | Risk | Rollback Time |
|---|---|---|---|
| **Rolling** | Standard update; small blast radius | Low | Minutes |
| **Blue/Green** | Zero-downtime; instant cutover or rollback | Medium | Seconds |
| **Canary** | High-risk changes; validate with subset of traffic | Low | Minutes |
| **Recreate** | Breaking changes; accept downtime window | High | N/A |
| **Feature flag** | Decouple deploy from release; gradual exposure | Very low | Instant |

Strategy selection rules: `references/deployment-strategies.md`

---

## Execution Protocol

**Step 1 — Validate Release Gate**
Confirm `release-readiness-confirmed` gate has PASS status in the memory packet.
Refuse to deploy if the gate is FAIL or NOT_EVALUATED.

**Step 2 — Select Target and Strategy**
Identify the deployment target (platform + environment). Select the deployment strategy
based on change risk, traffic volume, and team rollback tolerance.

**Step 3 — Produce Deployment Plan**
Emit a structured plan covering: target, strategy, pre-checks, execution steps, health
check criteria, rollback trigger, and estimated duration. Require operator approval
(Level 3) before proceeding.

**Step 4 — Run Pre-Deployment Checks**
Execute pre-checks: secrets present in target env, container image digests verified,
DNS resolves correctly, rollback artifact available, monitoring alerts armed.

**Step 5 — Execute Deployment**
Apply the deployment via the appropriate connector (Vercel API, kubectl, AWS CLI via MCP).
Monitor health check endpoints in real time during rollout.

**Step 6 — Confirm or Rollback**
If all health checks pass within the timeout: mark deployment CONFIRMED in the memory
packet. If any health check fails: immediately trigger rollback; create incident ticket;
alert on-call.

---

## Pre-Deployment Checklist

```
[ ] release-readiness-confirmed gate: PASS
[ ] Container image digest verified (matches release tag)
[ ] Secrets present in target environment (not expired)
[ ] Database migrations applied (if any)
[ ] Previous version artifact available for rollback
[ ] Health check endpoints defined and reachable
[ ] Monitoring alerts armed (Datadog / Sentry)
[ ] Deployment approved by operator (Level-3 gate)
[ ] Rollback procedure documented in deployment plan
[ ] DNS and CDN configuration verified
```

---

## Output Format

```
Deployment Plan
───────────────
Release:      [version]
Target:       [platform] / [environment]
Strategy:     [rolling | blue/green | canary | recreate]
Estimated Duration: [X minutes]
Operator Approval: REQUIRED

Pre-Checks:   [list with status]

Execution Steps:
  1. [step]
  2. [step]

Health Check:
  Endpoint: [URL]
  Timeout:  [N minutes]
  Success:  [HTTP 200, response contains X]

Rollback Trigger: health check fails after [N] minutes
Rollback Procedure: [steps]

Approval Reference: SEC-YYYYMMDD-NNN
```

---

## References

- `references/deployment-targets.md` — Platform configurations, required permissions, and connection setup
- `references/deployment-strategies.md` — Strategy selection rules, traffic routing, health check definitions