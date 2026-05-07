# Runtime Simulation Models Reference

## Simulation Model Catalog

### Model 1: Queuing Theory Model (M/M/K)

**Use for:** Estimating latency and throughput for inference services under load.

```
M/M/K queuing model assumptions:
  - Arrival process: Poisson (exponential inter-arrival times)
  - Service time: Exponential distribution
  - K servers (inference replicas)
  - Infinite queue capacity
  - FCFS discipline

Parameters:
  λ = arrival rate (requests per second)
  μ = service rate per server (requests per second per replica)
  K = number of replicas
  ρ = λ / (K × μ)  # Traffic intensity — must be < 1 for stable queue

Key metrics:
  Utilization: U = ρ = λ / (K × μ)
  P(wait > 0): Erlang-C(K, ρ)
  Average wait time: W_q = Erlang-C(K, ρ) / (K × μ × (1 - ρ))
  Average response time: W = W_q + 1/μ
  Average queue length: L_q = λ × W_q

Scaling recommendation:
  Target U ≤ 0.70 for interactive workloads (leaves headroom for bursts)
  For P99 latency SLO: solve for K such that P(W > SLO) < 0.01
```

### Model 2: Discrete Event Simulation (DES)

**Use for:** Complex workflow execution modeling with dependencies, retries, and conditional branches.

```python
class WorkflowDES:
    """
    Discrete event simulation of workflow execution.
    Models: step dependencies, parallel execution, retry behavior,
    checkpoint overhead, model routing decisions.
    """

    def simulate(self, workflow_spec, model_catalog, n_runs=1000):
        results = []

        for run in range(n_runs):
            # Sample model performance from calibrated distributions
            step_durations = {
                step.id: sample_step_duration(step, model_catalog)
                for step in workflow_spec.steps
            }

            # Execute dependency DAG
            execution_order = topological_sort(workflow_spec.dag)
            step_completions = {}

            for step_id in execution_order:
                step = workflow_spec.get_step(step_id)

                # Wait for all dependencies
                deps_complete_at = max(
                    step_completions.get(dep, 0)
                    for dep in step.dependencies
                ) if step.dependencies else 0

                # Add queuing wait time
                queue_wait = sample_queue_wait(
                    step.model_tier, deps_complete_at
                )

                # Execute step (with retry logic)
                duration = step_durations[step_id]
                failure_probability = step.failure_probability
                attempts = 0

                while True:
                    attempts += 1
                    if random() > failure_probability:
                        break  # Success
                    if attempts >= step.max_retries:
                        duration = float('inf')  # Workflow fails
                        break
                    duration += step.retry_delay

                step_completions[step_id] = deps_complete_at + queue_wait + duration

            total_duration = max(step_completions.values())
            results.append({
                'total_duration_s': total_duration,
                'step_completions': step_completions,
                'n_retries': sum(1 for d in step_durations.values() if d == float('inf'))
            })

        return SimulationResults(results)
```

### Model 3: Load Profile Simulation

**Use for:** Capacity planning — predicting resource requirements for anticipated load profiles.

```yaml
load_profile:
  id: "LOAD-PROD-2026-Q3"
  description: "Anticipated production load for Q3 2026"

  temporal_pattern:
    base_rps: 500  # Baseline requests per second
    peak_rps: 2000  # Peak during business hours
    peak_hours: "09:00-17:00 EST weekdays"
    off_peak_multiplier: 0.15  # Overnight
    weekly_seasonality: true
    monday_multiplier: 1.1  # Mondays slightly higher

  growth_model:
    growth_rate_monthly_pct: 12
    base_month: "2026-07"
    projection_months: 3

  request_mix:
    task_type_distribution:
      code_generation_simple: 0.25
      code_generation_complex: 0.20
      analysis_report: 0.30
      summarization: 0.15
      qa: 0.10

  resource_requirements_simulation:
    # Run DES with load profile to determine:
    required_replicas_p95:
      nano_tier: 4
      standard_tier: 8
      advanced_tier: 6
    peak_gpu_memory_gb: 640
    estimated_monthly_cost_usd: 28400
```

---

## Calibration Protocol

Before using simulation for production planning, calibrate against historical data:

```
CALIBRATION STEPS:
  1. Collect N ≥ 30 days of production metrics:
     - Request arrival rates (1-minute granularity)
     - Step execution durations (per model tier)
     - Queue wait times
     - Failure rates by step type

  2. Fit distributions:
     - Arrival: fit Poisson or Negative Binomial (if overdispersed)
     - Service time: fit log-normal (better tail fit than exponential)
     - Failure: fit Bernoulli per step type

  3. Validate:
     - Run simulation with fitted parameters on held-out 7-day period
     - Compare simulated P50, P95, P99 to actual
     - Calibration accepted if: simulated within 15% of actual across all percentiles

  4. Recalibrate quarterly or after significant workload changes
```

---

## Simulation Output Format

```yaml
simulation_result:
  simulation_id: "SIM-RUNTIME-20260507-001"
  model_type: "DES"
  n_runs: 5000
  workload: "LOAD-PROD-2026-Q3"

  workflow_duration:
    p50_seconds: 12.4
    p90_seconds: 28.1
    p95_seconds: 41.6
    p99_seconds: 89.3
    mean_seconds: 14.8
    std_seconds: 11.2

  failure_analysis:
    workflow_failure_rate: 0.003  # 0.3% of workflows fail
    most_common_failure_step: "advanced-model-inference"
    failure_cause: "model timeout after max retries"
    retry_success_rate: 0.87  # 87% of retried steps succeed

  capacity_recommendations:
    current_capacity_headroom_pct: 23
    recommended_buffer_pct: 30
    suggested_actions:
      - "Add 2 Advanced-tier inference replicas before Q3 peak"
      - "Implement request priority queue for P0 traffic"

  cost_estimate:
    compute_cost_per_1000_requests_usd: 0.034
    monthly_cost_at_peak_load_usd: 31200
```