---
name: business-continuity-planning
description: Authors Business Continuity Plans, runs DR simulations, monitors RTO/RPO targets, and maintains communication plans for enterprise resilience.
metadata:
  version: "0.1.0"
  category: resilience
  owner: platform
  maturity: draft
  dependencies: ['disaster-recovery-automation', 'governance']
---

## Role

Enterprise BCP lifecycle manager. Authors and maintains Business Continuity Plans for
the enterprise AI platform, coordinates DR simulation exercises, monitors ongoing RTO/RPO
target compliance, and maintains the communication plan for disaster scenarios. Bridges
the gap between DR execution capability (`disaster-recovery-automation`) and the governance
and planning requirements of enterprise resilience programs.

## Activation Triggers

- Annual BCP review cycle is due
- `disaster-recovery-automation` completes a drill and results require BCP update
- A new critical system is added that requires BCP coverage assessment
- `compliance-agent` requests BCP documentation for an audit
- Actual RTO/RPO achieved in a drill diverges from targets by > 20% (plan update required)

## Execution Protocol

1. **BCP authoring**: Generate and maintain the BCP document structure:
   - Business impact analysis (BIA): which systems/processes are business-critical, and at what RTO/RPO
   - Recovery strategies: DR approach per system (active-active, active-passive, backup-restore)
   - Dependencies: external vendor dependencies and their DR commitments
   - Communication plan: who is notified, in what order, via which channels, during a disaster

2. **Simulation scheduling**: Coordinate quarterly DR simulation calendar:
   - Schedule drills in `itsm-integration` as major change events
   - Assign simulation roles (incident commander, recovery lead, communications lead)
   - Prepare simulation scenarios with `disaster-recovery-automation`

3. **RTO/RPO monitoring**: Track actual vs. target RTO/RPO from each drill:
   - Maintain a historical RTO/RPO trend chart
   - Flag when actual > target × 1.2 (20% miss) → trigger BCP review
   - Surface metrics to `operator-console` and `compliance-agent`

4. **Communication plan execution**: During a declared disaster:
   - Trigger the stakeholder notification sequence via `notification-orchestration`
   - Maintain a real-time status update cadence (every 30 minutes during active incident)
   - Produce the post-incident communication (all-clear + summary)

5. **Post-drill review**: After each simulation, generate a lessons-learned report.
   Update BCP and DR runbooks with findings via `lessons-learned-extraction`.

## Output Format

```yaml
bcp_status:
  bcp_version: "2026.Q2.1"
  last_reviewed: "2026-05-07"
  next_review_due: "2026-08-07"
  rto_target_minutes: 30
  rpo_target_minutes: 15
  last_drill_rto_minutes: 28
  last_drill_rpo_minutes: 12
  drill_target_met: true
  critical_systems_covered: 0
  open_bcp_gaps: 0
```

## Quality Gates

- BCP must be reviewed and re-approved after every major architecture change
- All critical systems (RTO ≤ 4 hours) must have an executed DR runbook in `disaster-recovery-automation`

## References

- `references/` — BCP document template, BIA scoring rubric, RTO/RPO classification matrix
