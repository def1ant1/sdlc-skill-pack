# Deployment Targets

Used by `skills/cloud-deployment/SKILL.md` to define the configuration, required
permissions, and connection setup for each supported deployment platform.

---

## Vercel

| Property | Value |
|---|---|
| Connector | `vercel-api` |
| Deployment trigger | `POST /v13/deployments` or `vercel deploy --prod` via CLI |
| Rollback | `POST /v13/deployments/{id}/rollback` |
| Health check | Deployment URL returns HTTP 200 within 5 minutes of deploy |
| Environment secrets | Vercel dashboard → Project → Settings → Environment Variables |
| Required permissions | `deployments:write`, `projects:read` (via API token) |

**Key deploy flow:**
1. Push to linked Git branch (triggers automatic deploy) OR
2. Upload files directly via API (`POST /v13/deployments`)
3. Monitor build logs via `GET /v13/deployments/{id}`
4. Confirm production URL is live

---

## Cloudflare Workers / Pages

| Property | Value |
|---|---|
| Connector | `cloudflare-api` |
| Deploy Workers | `PUT /accounts/{account_id}/workers/scripts/{script_name}` |
| Deploy Pages | `POST /accounts/{account_id}/pages/projects/{project}/deployments` |
| Rollback | Set alias to previous deployment ID |
| Health check | Worker URL returns expected response within 2 minutes |
| Required permissions | Zone: Workers Scripts Edit, Pages: Edit |

**Key notes:**
- Workers deploy globally within ~30 seconds
- Pages deployments support preview URLs before production promotion
- Always test on preview before promoting to production alias

---

## AWS (ECS Fargate)

| Property | Value |
|---|---|
| Connector | `aws-api` (via MCP or Boto3) |
| Deploy command | Update ECS service with new task definition revision |
| Rollback | Update service to previous task definition revision |
| Health check | ALB target group health; ECS service stable check |
| Required IAM | `ecs:UpdateService`, `ecs:RegisterTaskDefinition`, `ecr:BatchGetImage` |
| Estimated rollout | Rolling: 5–15 min; Blue/Green: 2–5 min cutover |

**Deploy flow:**
1. Push container image to ECR (tagged with Git SHA)
2. Register new task definition revision
3. Update ECS service with new revision (rolling or CodeDeploy blue/green)
4. Wait for service to stabilize (`ecs:describe-services` stable state)

---

## GCP Cloud Run

| Property | Value |
|---|---|
| Connector | `gcp-api` |
| Deploy command | `gcloud run deploy {service} --image {image}` or API equivalent |
| Rollback | Route 100% traffic to previous revision |
| Health check | Cloud Run health check + liveness probe |
| Required roles | `run.developer` or `run.admin` |
| Traffic splitting | Native — canary via traffic split between revisions |

**Key advantage**: Traffic splitting between revisions makes Cloud Run ideal for
canary deployments without additional infrastructure.

---

## Kubernetes (self-hosted or EKS/GKE/AKS)

| Property | Value |
|---|---|
| Connector | `k8s-api` (via kubeconfig) |
| Deploy command | `kubectl apply -f deployment.yaml` or Helm upgrade |
| Rollback | `kubectl rollout undo deployment/{name}` |
| Health check | Deployment rollout status + readiness probes |
| Strategies | RollingUpdate (default), Recreate; Blue/Green via Service selector swap |

**Rolling update config:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

---

## Environment Promotion Order

All deployments must follow this promotion sequence:

```
development → staging → production
```

No artifact may skip staging. The staging deployment must pass its health check before
a production deployment is permitted. Production deployment always requires Level-3 approval.

---

## Rollback Decision Matrix

| Condition | Action | Timeline |
|---|---|---|
| Health check fails within 5 min of deploy | Automatic rollback | Immediate |
| Error rate spikes > 5× baseline post-deploy | Manual rollback trigger | < 10 min |
| Latency P95 doubles post-deploy | Manual rollback trigger | < 15 min |
| Business-critical feature broken | Manual rollback trigger | < 5 min |
| Minor degradation, workaround available | Create hotfix; do not roll back | — |