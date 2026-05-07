# Game Day Scenarios Reference

## Scenario Catalog

### Category 1: Infrastructure Failure Scenarios

#### INFRA-001: Regional Availability Zone Outage

```yaml
scenario:
  id: "INFRA-001"
  name: "AZ Failure — Primary Region"
  category: "infrastructure"
  severity: "P0"
  duration_minutes: 60
  participants: ["on-call SRE", "platform team lead", "incident commander"]

  inject:
    type: "network_partition"
    target: "availability_zone_us_east_1a"
    effect: "All EC2 instances, RDS primary, and ELBs in AZ become unreachable"
    start_time: "T+0"

  expected_response_timeline:
    T+5: "Alert fires: AZ health check fails across 3+ services"
    T+10: "Incident declared P0; incident commander assigned"
    T+15: "Traffic failover to AZ-B and AZ-C initiated"
    T+25: "RDS failover to standby in AZ-B complete"
    T+30: "Service restored; verification of full traffic routing"
    T+45: "Post-incident documentation started"

  learning_objectives:
    - "Validate AZ failover runbook accuracy"
    - "Test RDS multi-AZ failover timing (target: < 30s)"
    - "Confirm all services have cross-AZ health checks"
    - "Verify on-call rotation coverage for P0 response"

  inject_signals:
    - CloudWatch: AZ health check RED for us-east-1a
    - Datadog: 5xx rate spike on all services
    - PagerDuty: P0 alert triggered

  success_criteria:
    time_to_detect_minutes: ≤ 5
    time_to_declare_incident_minutes: ≤ 10
    time_to_restore_minutes: ≤ 30
    customer_impact_duration_minutes: ≤ 20
```

---

#### INFRA-002: Database Connection Pool Exhaustion

```yaml
scenario:
  id: "INFRA-002"
  name: "DB Connection Pool Exhaustion"
  severity: "P1"
  duration_minutes: 30

  inject:
    type: "synthetic_load"
    target: "api_service"
    effect: "500 concurrent requests all holding DB connections for 30s"

  learning_objectives:
    - "Validate connection pool monitoring alerts fire before exhaustion"
    - "Test circuit breaker trip behavior"
    - "Confirm graceful degradation (queue vs. reject)"
```

---

### Category 2: Security Incident Scenarios

#### SEC-001: Credential Compromise Simulation

```yaml
scenario:
  id: "SEC-001"
  name: "Compromised Service Account"
  category: "security"
  severity: "P1"
  participants: ["security team", "platform team", "incident commander"]

  inject:
    type: "policy_simulation"  # No actual credential compromise
    simulated_signals:
      - "AWS CloudTrail: unusual API calls from service account SA-API-PROD"
      - "API calls from unexpected region: eu-west-2 (not in baseline)"
      - "ListBuckets and GetObject on sensitive S3 buckets"

  expected_response_timeline:
    T+0: "SIEM alert fires: anomalous API activity"
    T+5: "Security on-call acknowledges; starts investigation"
    T+10: "Service account suspended pending investigation"
    T+15: "Blast radius assessment: which systems used this credential"
    T+25: "Incident scoped: no data exfiltration confirmed"
    T+30: "New credential issued; access restored with scope reduction"

  learning_objectives:
    - "Test credential rotation runbook under pressure"
    - "Validate blast radius identification tooling"
    - "Confirm SIEM alert quality (signal vs. noise)"
```

---

### Category 3: Data Pipeline Failure Scenarios

#### DATA-001: Training Data Pipeline Corruption

```yaml
scenario:
  id: "DATA-001"
  name: "Silent Data Corruption in ML Pipeline"
  category: "data"
  severity: "P1"
  duration_minutes: 45

  inject:
    type: "data_quality_inject"
    target: "feature_store_pipeline"
    effect: "5% of feature vectors have NaN values injected silently"
    detection_difficulty: "HIGH"  # No immediate failures; degraded model performance

  expected_detection:
    method: "model performance monitoring"
    signal: "Accuracy drops 3% over 48h rolling window"
    alert_threshold: "accuracy_delta > -0.02 over 24h"

  learning_objectives:
    - "Test data quality monitoring coverage"
    - "Validate ML pipeline rollback procedure"
    - "Confirm lineage tracing identifies corrupted batch"
```

---

### Category 4: Capacity and Scaling Scenarios

#### CAP-001: Unexpected Traffic Spike

```yaml
scenario:
  id: "CAP-001"
  name: "10× Traffic Spike — Product Launch"
  category: "capacity"
  severity: "P1"
  duration_minutes: 30

  inject:
    type: "synthetic_load"
    ramp_profile: "step_function"
    baseline_rps: 1000
    spike_rps: 10000
    ramp_time_seconds: 60

  expected_response:
    auto_scaling_trigger_seconds: ≤ 120
    traffic_shed_acceptable: true  # Some requests may be rejected during ramp
    full_capacity_seconds: ≤ 300
    no_data_loss: true

  learning_objectives:
    - "Validate auto-scaling speed and target capacity"
    - "Test CDN and load balancer behavior under spike"
    - "Confirm database read replicas scale with load"
```

---

## Scenario Execution Protocol

```
PRE-GAME DAY (T-7 days):
  □ Distribute scenario description to participants (WITHOUT inject details)
  □ Confirm all participants' roles and responsibilities
  □ Verify safety controls are in place (rollback procedures, kill switch)
  □ Confirm monitoring dashboards are accessible
  □ Brief incident commander on scenario safety boundaries

GAME DAY EXECUTION:
  T-15: Briefing — "Today we will simulate [incident type]. Your job is to respond as you would in production."
  T+0: Inject deployed by facilitator
  T+X: Facilitator observes, takes notes, does NOT help (except safety boundary violations)
  T+end: Inject removed; facilitator calls "END EXERCISE"

POST-GAME DAY (same day):
  □ Hot wash (30 min): immediate reactions, what worked, what didn't
  □ Capture findings in structured format
  □ Assign action items with owners and due dates

T+5 days:
  □ Publish post-exercise report
  □ Track action item completion in issue tracker
```

---

## Findings Classification

| Finding Type | Description | SLA for Remediation |
|---|---|---|
| CRITICAL | Safety boundary violated or incident response failed completely | 7 days |
| HIGH | Detection or response time SLO missed by > 50% | 30 days |
| MEDIUM | Runbook gap, tooling issue, or coordination failure | 60 days |
| LOW | Minor process improvement or documentation update | 90 days |
| OBSERVATION | Positive finding or best practice identified | N/A |