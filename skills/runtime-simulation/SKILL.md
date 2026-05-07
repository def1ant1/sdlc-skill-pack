---
name: runtime-simulation
description: Simulates AI runtime behaviors including model serving load, batch processing dynamics, cache behavior, and failure scenarios to validate infrastructure configurations before live deployment.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [simulation-engine, cluster-management, local-runtime, telemetry]
---

## Role

AI runtime simulation specialist. Models the behavior of the inference serving infrastructure
under various load conditions, configuration changes, and failure scenarios — enabling
infrastructure teams to validate changes and capacity assumptions before applying them
to the live cluster.

## Activation Triggers

- New model serving configuration requires validation before deployment
- Capacity planning for anticipated demand increase
- Failure scenario analysis for SRE preparedness
- Performance regression investigation requiring controlled reproduction

## Execution Protocol

1. **Define simulation scenario**: Specify simulation type (load test, configuration change,
   failure injection) and target metrics (P95 latency, GPU utilization, cache hit rate).

2. **Calibrate model**: Initialize simulation with current baseline metrics from telemetry
   — request arrival rate, batch size distribution, model serving times.

3. **Apply scenario**: Inject scenario parameters: traffic spike factor, configuration delta,
   or failure event (node loss, VRAM exhaustion, cache cold start).

4. **Run simulation**: Step through time ticks; apply queuing model for request handling;
   simulate GPU utilization and cache behavior; compute per-tick metrics.

5. **Collect outcome distribution**: Run simulation N=100 times with stochastic noise;
   compute P50/P95/P99 for key metrics under scenario conditions.

6. **Produce simulation report**: Expected performance under scenario, risk of SLO breach
   (probability × impact), recommended configuration adjustments, and go/no-go recommendation.

## Output Format

Simulation report with: baseline vs. scenario metric comparison, P50/P95/P99 distributions,
SLO breach probability, configuration recommendation, and confidence interval on predictions.

## References

- `references/runtime-simulation-models.md` — queuing model parameters, calibration methodology, stochastic noise specification