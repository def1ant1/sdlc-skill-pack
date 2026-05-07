# Business Continuity Planning — BCP Framework

## BCP Scope & Objectives

| Objective | Target |
|-----------|--------|
| Recovery Time Objective (RTO) | Platform: 60 min; Critical services: 15 min |
| Recovery Point Objective (RPO) | Tier-1 data: 5 min; Tier-2 data: 60 min |
| Maximum Tolerable Downtime (MTD) | 4 hours for any P1 service |
| Annual BCP test cadence | Full DR drill: 2× per year; Tabletop: quarterly |

---

## Business Impact Analysis (BIA) Schema

```yaml
business_impact_analysis:
  bia_id: "BIA-2026-xxxxx"
  assessed_at: "2026-05-07T00:00:00Z"
  assessment_period_months: 12

  process_assessments:
    - process_id: "PROC-inference-serving"
      process_name: "AI Inference Serving"
      owner: "sre-agent"
      criticality: tier-1   # tier-1 (critical) | tier-2 | tier-3

      dependencies:
        - CI-inference-fleet
        - CI-zero-trust-runtime
        - CI-api-gateway

      rto_minutes: 15
      rpo_minutes: 5
      mtd_hours: 2

      impact_if_unavailable:
        financial_per_hour_usd: 50000
        regulatory_risk: medium
        reputational_risk: high
        affected_customers_pct: 100

    - process_id: "PROC-compliance-monitoring"
      process_name: "Continuous Compliance Monitoring"
      owner: "compliance-agent"
      criticality: tier-2
      rto_minutes: 240
      rpo_minutes: 60
      mtd_hours: 24
      impact_if_unavailable:
        financial_per_hour_usd: 5000
        regulatory_risk: high
        reputational_risk: medium
        affected_customers_pct: 10
```

---

## BCP Plan Schema

```yaml
bcp_plan:
  plan_id: "BCP-2026-xxxxx"
  plan_name: "Apotheon Platform — Business Continuity Plan v3.0"
  version: "3.0"
  effective_date: "2026-05-07"
  next_review_date: "2026-11-07"
  owner: "program-governance-agent"
  approved_by: "cto"

  scope:
    covered_processes:
      - PROC-inference-serving
      - PROC-compliance-monitoring
      - PROC-data-ingestion
    excluded_processes:
      - PROC-internal-hr-tools   # Separate BCP

  risk_scenarios:
    - scenario_id: "SCEN-001"
      name: "Primary cloud region outage"
      probability: low
      impact: critical
      rto_target_minutes: 60

    - scenario_id: "SCEN-002"
      name: "Key personnel unavailability (> 50% team)"
      probability: very_low
      impact: high
      rto_target_minutes: 240

    - scenario_id: "SCEN-003"
      name: "Ransomware / data corruption event"
      probability: low
      impact: critical
      rto_target_minutes: 120

  activation_criteria:
    - "P1 incident declared lasting > 30 min with no clear resolution path"
    - "Primary region declared unavailable by cloud provider"
    - "Security incident with confirmed data exfiltration"
    - "Explicit decision by on-call SRE lead or CTO"

  activation_authority:
    - title: "On-call SRE Lead"
      can_activate: true
    - title: "CTO"
      can_activate: true
    - title: "program-governance-agent"
      can_activate: false   # Can recommend; human must activate
```

---

## Recovery Playbooks (Summary)

### Playbook 1: Cloud Region Failover

```
1. Declare BCP active (on-call SRE Lead)
2. Notify stakeholders via notification-orchestration
3. Switch DNS to DR region (pre-configured)
4. Verify DR inference fleet health (automated smoke test)
5. Scale DR fleet to production capacity
6. Validate data consistency (last RPO checkpoint)
7. Update status page to "operating from DR region"
8. Initiate hourly executive updates via executive-reporting
Target: < 60 min RTO
```

### Playbook 2: Data Corruption Recovery

```
1. Isolate affected systems (block writes)
2. Identify corruption scope (last clean checkpoint)
3. Restore from immutable backup (GCS versioned)
4. Validate restored data integrity (checksum + spot checks)
5. Resume writes
6. Replay any lost transactions from WAL (if within RPO)
7. Post-incident review within 24 hours
Target: < 120 min RTO; < 5 min RPO
```

---

## BCP Test Schema

```yaml
bcp_test:
  test_id: "BCP-TEST-2026-xxxxx"
  test_type: tabletop | simulation | full_failover
  scenario_id: "SCEN-001"
  conducted_at: "2026-05-07T09:00:00Z"
  participants: [sre-lead, cto, program-governance-agent, compliance-agent]

  objectives:
    - "Verify RTO ≤ 60 min for inference serving under region outage scenario"
    - "Confirm all activation communication steps execute correctly"

  results:
    rto_achieved_minutes: 47
    rto_target_minutes: 60
    rto_met: true

    rpo_achieved_minutes: 3
    rpo_target_minutes: 5
    rpo_met: true

    issues_identified:
      - "DNS propagation took 8 min due to high TTL — reduce TTL to 60s"
      - "Status page update was manual — automate via monitoring-agent"

  action_items:
    - task: "Reduce DNS TTL for api.apotheon.io from 300s to 60s"
      owner: "sre-agent"
      due: "2026-05-14"
    - task: "Automate status page updates on BCP activation"
      owner: "infrastructure-optimization-agent"
      due: "2026-05-21"

  overall_rating: pass   # pass | pass_with_findings | fail
```

---

## BCP Documentation Maintenance Policy

| Document | Trigger for Update | Review Owner |
|----------|-------------------|-------------|
| BIA | Service criticality change or annual | program-governance-agent |
| BCP Plan | Any scenario addition or RTO/RPO change | CTO |
| Recovery Playbooks | Post-incident RCA recommendations | sre-agent |
| BCP Test Results | After each test | program-governance-agent |

All BCP documents stored in `gs://apotheon-bcp-docs/` with versioning enabled. Previous versions retained for 7 years (compliance requirement).