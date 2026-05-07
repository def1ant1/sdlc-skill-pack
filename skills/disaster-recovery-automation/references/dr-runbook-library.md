# DR Runbook Library

## Runbook: Region Outage (RUNBOOK-REGION-001)

```yaml
runbook_id: RUNBOOK-REGION-001
scenario: region_outage
rto_target_minutes: 30
rpo_target_minutes: 15

steps:
  - step: 1
    name: "Declare disaster and freeze primary region writes"
    type: automated
    action: "Set primary region to READ_ONLY mode via cluster-management API"
    timeout_minutes: 2
    rollback_action: "Restore primary region to READ_WRITE mode"

  - step: 2
    name: "Verify secondary region health"
    type: automated
    action: "Run health check suite against all P0 services in secondary region"
    pass_criterion: "All P0 services return healthy"
    timeout_minutes: 5
    on_failure: "Page incident commander immediately — failover blocked"

  - step: 3
    name: "Identify latest valid backup snapshot"
    type: automated
    action: "Query backup store for latest snapshot with timestamp <= RPO window"
    pass_criterion: "Snapshot age <= rpo_target_minutes"
    timeout_minutes: 2
    on_failure: "Escalate — RPO breach risk; requires executive decision"

  - step: 4
    name: "Restore database from snapshot to secondary region"
    type: automated
    action: "Trigger restore job from backup snapshot to secondary database cluster"
    timeout_minutes: 15
    monitor: true

  - step: 5
    name: "Execute DNS cutover to secondary region"
    type: automated
    action: "Update DNS A records and load balancer targets to secondary region endpoints"
    timeout_minutes: 3
    monitor_dns_propagation: true

  - step: 6
    name: "Warm up inference engine fleet in secondary region"
    type: automated
    action: "Start inference engine replicas in secondary region; run warmup validation"
    timeout_minutes: 5

  - step: 7
    name: "Run recovery validation suite"
    type: automated
    action: "Execute full recovery validation test suite"
    pass_criterion: "All P0 services healthy; data integrity check passes"
    timeout_minutes: 5
    on_failure: "Halt and alert — recovery not validated"

  - step: 8
    name: "Declare recovery complete"
    type: manual
    action: "Incident commander confirms recovery and sends all-clear"
    timeout_minutes: 5

  - step: 9
    name: "Send stakeholder all-clear communication"
    type: automated
    action: "Trigger all-clear notification via notification-orchestration"
    timeout_minutes: 2
```

---

## Runbook: Database Failure (RUNBOOK-DB-001)

```yaml
runbook_id: RUNBOOK-DB-001
scenario: database_failure
rto_target_minutes: 15
rpo_target_minutes: 5

steps:
  - step: 1
    name: "Detect failure type"
    type: automated
    action: "Classify failure: primary node failure vs. replication lag vs. data corruption"

  - step: 2
    name: "Automatic replica promotion (primary node failure only)"
    type: automated
    action: "Promote the most up-to-date replica to primary via cluster-management"
    condition: "failure_type == primary_node_failure"
    timeout_minutes: 3

  - step: 3
    name: "Restore from backup (data corruption detected)"
    type: automated
    action: "Identify the last clean backup before corruption timestamp; restore"
    condition: "failure_type == data_corruption"
    timeout_minutes: 10

  - step: 4
    name: "Verify data integrity"
    type: automated
    action: "Run integrity checks: record counts, referential integrity, hash verification"
    timeout_minutes: 3

  - step: 5
    name: "Resume write traffic"
    type: automated
    action: "Restore database to READ_WRITE mode; drain the write queue"
    timeout_minutes: 2
```

---

## Recovery Validation Test Suite

```yaml
validation_suite:
  - test_id: RVT-001
    name: "P0 service health checks"
    type: http_health_check
    targets:
      - "https://api.enterprise-os.internal/health"
      - "https://auth.enterprise-os.internal/health"
      - "https://inference.enterprise-os.internal/health"
    pass_criterion: "All return HTTP 200 within 2 seconds"

  - test_id: RVT-002
    name: "Database record count integrity"
    type: data_integrity
    action: "Compare record counts in critical tables against pre-disaster snapshot"
    pass_criterion: "Record count delta < 0.001% (RPO window tolerance)"

  - test_id: RVT-003
    name: "Inference engine end-to-end test"
    type: functional_test
    action: "Submit a test completion request; verify response is valid"
    pass_criterion: "Valid response returned within p95 latency SLO"

  - test_id: RVT-004
    name: "Agent fleet reconnection"
    type: functional_test
    action: "Verify all persistent agents have reconnected and resumed heartbeats"
    pass_criterion: "persistent-agent-runtime reports all agents HEALTHY within 5 minutes"

  - test_id: RVT-005
    name: "Authentication flow"
    type: functional_test
    action: "Perform a full mTLS handshake and JWT acquisition"
    pass_criterion: "JWT returned and accepted by zero-trust-runtime"
```

---

## Chaos Test Scenarios

| Scenario ID | Description | Blast Radius | RTO Impact |
|------------|-------------|--------------|------------|
| CHAOS-001 | Random pod termination (1 pod/min) | Single service | Low |
| CHAOS-002 | Primary database node kill | Database cluster | High — tests failover |
| CHAOS-003 | Network partition (50% packet loss between regions) | Cross-region traffic | High — tests routing |
| CHAOS-004 | CPU saturation (inference engine fleet at 95%) | Inference serving | Medium — tests autoscaling |
| CHAOS-005 | Secrets vault unavailability (5 minutes) | New authentications | High — tests cached token grace period |

---

## RTO/RPO Tracking

```yaml
rto_rpo_history:
  - drill_id: "DRILL-2026-Q1"
    date: "2026-03-15"
    scenario: region_outage
    actual_rto_minutes: 28
    target_rto_minutes: 30
    met_rto: true
    actual_rpo_minutes: 12
    target_rpo_minutes: 15
    met_rpo: true
    gaps_identified: ["Step 4 (DB restore) took 2m longer than estimated due to snapshot size growth"]
```