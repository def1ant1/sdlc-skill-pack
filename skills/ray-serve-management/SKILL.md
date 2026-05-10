---
name: ray-serve-management
description: Manages Ray Serve deployments with autoscaling, canary routing, and traffic splitting for the inference serving layer.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['ray-runtime', 'inference-engine-fleet']

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

## Role

Ray Serve deployment manager. Handles the full lifecycle of Ray Serve deployments including
initial deployment, configuration updates, canary rollouts, A/B traffic splitting, and
graceful scale-in. Provides a higher-level deployment API on top of `ray-runtime` for
serving-specific workflows.

## Activation Triggers

- A new model serving endpoint is required on the Ray Serve layer
- A serving deployment requires a configuration update (new model, changed replicas, timeout)
- A canary rollout is initiated for a new model version
- A/B traffic split is required for `workflow-ab-testing` or `reinforcement-optimizer`
- A deployment health check fails and requires rollback
- Operator requests a replica count adjustment for a specific deployment

## Execution Protocol

1. **Deployment definition**: Parse a Ray Serve deployment spec:
   - `deployment_name`, `route_prefix`
   - `replica_config`: min_replicas, max_replicas, target_ongoing_requests (autoscaling)
   - `model_config`: model path, batch size, max concurrent queries
   - `health_check_period_s`, `graceful_shutdown_wait_s`

2. **Deploy**: Submit deployment to Ray Serve via `ray-runtime`. Wait for min_replicas
   to reach RUNNING status. Verify endpoint responds to health probe.

3. **Canary rollout**: For version updates:
   a. Deploy new version alongside existing as a separate deployment
   b. Route 5% of traffic to the new version via Ray Serve's `@serve.ingress` router
   c. Monitor error rate and p95 latency on the canary for 15 minutes
   d. If metrics are within SLO: gradually shift traffic (5% → 25% → 50% → 100%)
   e. If metrics breach SLO: immediately route 100% back to stable version and alert

4. **Autoscaling**: Configure Ray Serve's built-in autoscaler with:
   `target_ongoing_requests` as the scaling metric. Set `upscale_delay_s` and `downscale_delay_s`
   to avoid thrashing.

5. **Delete/scale-to-zero**: On operator request, gracefully drain and delete a deployment.
   Wait for in-flight requests to complete up to `graceful_shutdown_wait_s`.

## Output Format

```yaml
serve_deployment:
  deployment_name: "llama3-70b-instruct"
  route_prefix: "/v1/llama3-70b"
  status: RUNNING | DEPLOYING | UNHEALTHY | DELETING
  replicas:
    running: 4
    starting: 0
    failed: 0
  canary:
    active: false
    canary_traffic_pct: 0
    canary_status: null
  autoscaling_metric: "ongoing_requests"
  p95_latency_ms: 0
```

## Quality Gates

- Canary must receive ≥ 100 requests before promotion decision
- Rollback must complete within 60 seconds of SLO breach detection

## References

- `references/` — Deployment spec schema, canary rollout policy, autoscaling configuration
