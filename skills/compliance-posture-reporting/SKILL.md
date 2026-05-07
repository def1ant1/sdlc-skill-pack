---
name: compliance-posture-reporting
description: Generates regulator-ready compliance reports, gap analyses, and remediation tracking dashboards from compliance-runtime posture data.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: draft
  dependencies: ['compliance-runtime', 'continuous-control-monitoring']
---

## Role

Compliance reporting and visualization layer. Transforms raw control evaluation results
and posture scores from `compliance-runtime` into structured reports for regulators,
auditors, executives, and internal compliance teams. Tracks open gaps through remediation
and maintains a current audit-readiness posture dashboard.

## Activation Triggers

- An external audit is scheduled and requires a comprehensive evidence package
- Monthly/quarterly compliance posture report is due for executive review
- A control status changes (new failure → impact report; new passing → improvement report)
- `compliance-agent` requests a gap analysis for a specific framework
- An operator requests an ad-hoc posture snapshot for a specific framework or control domain

## Execution Protocol

1. **Posture snapshot**: Pull the current control evaluation results from `compliance-runtime`
   for the requested framework(s). Compute:
   - Overall posture score (%)
   - Posture trend vs. prior period (improving / stable / degrading)
   - Control status breakdown (passing / failing / not_tested / not_applicable)

2. **Gap analysis**: For all FAILING controls:
   - Classify gap severity: Critical (audit finding likely), High, Medium, Low
   - Identify gap owner and current remediation status
   - Estimate remediation timeline based on open itsm-integration tasks
   - Compute audit risk score: `P(material finding) = f(gap severity, auditor focus area)`

3. **Remediation tracking**: For each open gap, track:
   - Remediation task reference in `itsm-integration`
   - Target remediation date
   - Days overdue (if past target date)
   - Escalation status (None / Escalated to compliance-agent / Escalated to CISO)

4. **Report generation**: Produce reports in appropriate format for the audience:
   - **Auditor package**: full evidence manifest, control-by-control status table, evidence links
   - **Executive summary**: posture scores by framework, trend chart, top 3 risks, remediation progress
   - **Operational dashboard**: live posture scores, gap count by severity, SLA attainment

5. **Evidence packaging**: For external auditor delivery, compile evidence artifacts into
   a structured package: control ID → status → evidence artifact → collection timestamp.
   Generate a manifest with SHA-256 hashes for tamper detection.

## Output Format

```yaml
compliance_report:
  report_id: "RPT-SOC2-2026-Q2"
  framework: soc2
  generated_at: "2026-05-07T10:00:00Z"
  posture_score: 0.0
  posture_trend: improving | stable | degrading
  controls_passing: 0
  controls_failing: 0
  open_gaps:
    critical: 0
    high: 0
    medium: 0
  remediation_on_track: true
  audit_readiness_pct: 0.0
  evidence_package_ref: null
```

## Quality Gates

- Auditor packages must include evidence freshness dates — no stale evidence delivered
- Critical gaps must be flagged in all reports regardless of audience

## References

- `references/` — Report template library, gap severity classification, evidence package manifest schema
