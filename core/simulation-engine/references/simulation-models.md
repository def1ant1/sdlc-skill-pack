# Simulation Model Catalog

## Overview

Defines simulation model types available in the simulation-engine, selection guide,
parameterization requirements, validation criteria, and output format standards.

---

## Simulation Model Types

### 1. Monte Carlo Simulation

**Description:** Runs N trials sampling from probability distributions over uncertain
inputs; aggregates results into outcome distributions.

**Best for:**
- Financial risk and scenario analysis
- Business outcome forecasting with uncertain assumptions
- Project schedule risk quantification
- Insurance and actuarial modeling

**Parameterization requirements:**
- Input variable probability distributions (type, mean, std dev or bounds)
- Number of trials (minimum 1,000; default 10,000; recommend 100,000 for tail risk)
- Correlation matrix between input variables (if correlations exist)
- Outcome metric formula (how inputs combine to produce the output)

**Validation criteria:**
- Convergence test: P50 and P90 values stable within 1% across runs
- Distribution fit test: verify assumed distributions fit historical data (KS test p > 0.05)
- Sensitivity test: Tornado chart identifies top 3 drivers as expected

---

### 2. Agent-Based Simulation

**Description:** Models a system as a population of autonomous agents interacting
according to defined rules; emergent behavior is observed from local interactions.

**Best for:**
- Market dynamics and competitive strategy simulation
- Social contagion and adoption modeling
- Supply chain disruption analysis
- Multi-agent coordination testing before production deployment

**Parameterization requirements:**
- Agent type definitions (behavior rules, initial state distribution)
- Environment definition (space, resources, interaction rules)
- Tick duration and total simulation steps
- Population size (recommend ≥ 100 agents for statistical validity)

**Validation criteria:**
- Baseline calibration: known historical outcome reproduced within 10%
- Sensitivity test: results stable to ±20% perturbation in key parameters
- Edge case test: extreme parameter values produce expected limiting behavior

---

### 3. Discrete-Event Simulation

**Description:** Models a system as a sequence of discrete events occurring at
specific times; resource utilization and queuing behavior are primary outputs.

**Best for:**
- Infrastructure capacity planning (server queues, inference batching)
- Manufacturing process optimization
- Healthcare patient flow analysis
- Customer service staffing optimization

**Parameterization requirements:**
- Event types and inter-arrival time distributions
- Service time distributions per event type
- Resource pool definitions (count, capacity, scheduling discipline)
- Simulation warm-up period and run length

**Validation criteria:**
- Queue length and wait time match historical observations within 15%
- Utilization rates for all resources within 5% of historical measurements
- Sensitivity to ±10% change in arrival rate produces expected directional response

---

### 4. System Dynamics

**Description:** Models a system as stocks and flows with feedback loops; captures
dynamic behavior over time including oscillations and equilibria.

**Best for:**
- Long-horizon strategic planning (market share dynamics, technology adoption)
- Supply chain bullwhip effect analysis
- Organizational growth and resource constraints
- Environmental or sustainability modeling

**Parameterization requirements:**
- Stock variable initial values
- Flow rate equations (including feedback loop structure)
- Delay parameters (pipeline and information delays)
- Time step (dt) — must be < smallest delay / 4 for numerical stability

**Validation criteria:**
- Reference mode behavior: simulation replicates known historical behavior pattern
- Extreme conditions test: system responds appropriately to extreme parameter values
- Policy sensitivity: known effective policies produce expected improvement in model

---

### 5. Digital Twin (Runtime Behavior Simulation)

**Description:** A real-time digital replica of the AI infrastructure that mirrors
current state and simulates proposed changes before production application.

**Best for:**
- Pre-deployment validation of configuration changes
- Capacity planning and "what-if" analysis for infrastructure
- Failure injection testing in a safe environment
- AI safety scenario testing (simulate constitutional violations, escalation behavior)

**Parameterization requirements:**
- Current production telemetry snapshot (source of truth for initial state)
- Proposed change specification
- Simulation duration (how far ahead to project)
- Fidelity level (high fidelity = 1:1 agent behavior; low fidelity = statistical approximation)

**Validation criteria:**
- Digital twin must match production metrics within 5% over a 24-hour retrospective period
- Change simulation is only trusted if retrospective validation passes

---

## Simulation Selection Guide

| Scenario | Recommended Model | Rationale |
|---|---|---|
| "What are the odds of this project completing on time?" | Monte Carlo | Uncertainty quantification |
| "How will our agents behave when coordinating on this task?" | Agent-Based | Emergent coordination dynamics |
| "How will our inference queue behave at 2× traffic?" | Discrete-Event | Queuing and resource utilization |
| "What happens to market share over 5 years if we enter this segment?" | System Dynamics | Feedback loops and time delays |
| "Will this configuration change break production?" | Digital Twin | Real state, real behavior mirror |

---

## Output Format Standards

All simulation outputs include:

```yaml
simulation_result:
  simulation_id: "SIM-20260507-001"
  model_type: "monte-carlo"
  run_timestamp: "2026-05-07T14:23:00Z"
  trials: 10000
  convergence_test: passed

  outcome_distributions:
    - metric: "project_completion_days"
      p10: 45
      p25: 52
      p50: 60
      p75: 71
      p90: 85
      mean: 62.3
      std_dev: 14.1

  scenario_summaries:
    - name: "optimistic"
      definition: "P10 outcome on all key inputs"
      outcome: {project_completion_days: 45}
    - name: "base"
      definition: "P50 on all key inputs"
      outcome: {project_completion_days: 60}
    - name: "pessimistic"
      definition: "P90 on all key inputs"
      outcome: {project_completion_days: 85}

  sensitivity_analysis:
    top_drivers:
      - variable: "developer_productivity"
        impact_on_p90: "+12 days per -10% productivity"
      - variable: "scope_growth_rate"
        impact_on_p90: "+8 days per +10% scope"

  validation_results:
    convergence: passed
    distribution_fit: passed
    sensitivity_direction: passed
```