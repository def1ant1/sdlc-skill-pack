---
name: incident-simulation
description: Designs and runs game day exercises for SRE and security teams by injecting realistic failure scenarios into simulation environments, measuring response effectiveness, and producing preparedness improvement plans.
metadata:
  version: "1.0.0"
  category: simulation
  owner: sre
  maturity: alpha
  dependencies: [simulation-engine, sre, telemetry]
---

## Role

Game day exercise designer and runner for SRE and security preparedness. Generates realistic
failure scenario scripts, coordinates simulation execution in isolated environments, measures
team response effectiveness against SLO targets, and produces structured improvement plans
for gaps discovered during the exercise.

## Activation Triggers

- Scheduled quarterly game day exercise for an SRE or security team
- Post-incident review identifies a preparedness gap requiring a targeted drill
- New infrastructure component or runbook requires validation through simulation
- Security-war-gaming skill requests an incident response drill for a specific threat scenario

## Execution Protocol

1. **Define exercise scope**: Select the failure scenario type — node failure, network partition,
   database corruption, security breach, traffic spike, or cascading failure — and the target
   system under test.

2. **Generate scenario script**: Produce a detailed exercise script with: initial conditions,
   failure injection sequence, expected system behaviors, and observable symptoms for
   participants to detect.

3. **Configure simulation environment**: Provision an isolated simulation instance; inject
   the defined failure conditions using simulation-engine fault injection primitives; confirm
   isolation from production.

4. **Run exercise**: Execute the scenario; observe and record team response actions, time-to-detect,
   time-to-mitigate, runbook adherence, and communication effectiveness.

5. **Measure effectiveness**: Compare actual response metrics (TTD, TTM, error rate) against
   target SLOs; score runbook adherence; identify missed detection signals and delayed
   response decision points.

6. **Produce preparedness report**: Document findings, gaps, and a prioritized improvement
   plan — runbook updates, monitoring rule additions, training recommendations.

## Output Format

Game day report with: `exercise_id`, `scenario_type`, `time_to_detect` (minutes), `time_to_mitigate`
(minutes), `slo_adherence` (%), `runbook_adherence_score`, `gaps_identified` (list),
and `improvement_plan` (prioritized recommendations).

## References

- `references/game-day-scenarios.md` — failure scenario library, injection primitives, SLO benchmarks by system type