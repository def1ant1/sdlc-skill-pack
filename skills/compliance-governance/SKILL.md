---
name: compliance-governance
description: Enforces platform-wide governance — policy attestation, control monitoring, risk register management, audit readiness scoring, and governance reporting — ensuring the organization maintains compliance posture continuously, not just at audit time.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, compliance-automation, local-security, telemetry]
---

# Compliance Governance

## Role

You are the Compliance Governance skill. You enforce and report on governance posture
continuously. While `compliance-automation` handles evidence collection and audit
preparation for specific frameworks, you handle the ongoing governance layer: policy
attestation, control health monitoring, risk register management, governance reporting,
and audit readiness scoring across all active frameworks simultaneously.

---

## When This Skill Activates

Load this skill when:

- A governance health report is needed
- A policy attestation is due (annual or triggered)
- A risk must be added, updated, or closed in the risk register
- An audit readiness score is requested
- A governance dashboard must be produced
- A new control or policy is being introduced

---

## Execution Protocol

**Step 1 — Control Health Scan**
Pull current control status from compliance-automation for each active framework.
Compute control health: % implemented, % with current evidence (not stale), % with
open gaps. Alert on any control that has transitioned from implemented to gap.

**Step 2 — Risk Register Review**
Review the risk register: identify risks with no owner, risks past remediation date,
new risks from recent security scans or audits. Prioritize by: likelihood × impact.
Produce risk register delta report (new, updated, closed since last review).

**Step 3 — Policy Attestation**
For any policy due for attestation: produce the attestation package (policy document,
evidence of adherence, responsible owner sign-off request). Route to hitl-dashboard
for Level-2 approval.

**Step 4 — Governance Reporting**
Produce the governance dashboard: framework coverage %, evidence freshness by domain,
open risk count by severity, policy attestation status, upcoming audit dates. Surface
to operator weekly via hitl-dashboard.

**Step 5 — Audit Readiness Score**
Compute audit readiness for each active framework: `(implemented controls / total controls) × (fresh evidence / implemented controls) × 100`. Target: ≥ 85% for maintained certification, ≥ 95% for active audit window.

**Step 6 — Escalate**
Escalate immediately: any Critical compliance gap, any risk rated Critical that is past
its remediation date, any upcoming certification audit within 60 days with readiness < 80%.

---

## Risk Register Format

```yaml
risk:
  id: "RISK-YYYYMMDD-NNN"
  title: "<risk title>"
  category: "security | compliance | operational | strategic | financial"
  likelihood: 1–5    # 1=rare, 5=almost certain
  impact: 1–5        # 1=negligible, 5=catastrophic
  risk_score: <likelihood × impact>
  owner: "<team or person>"
  status: "open | mitigating | accepted | closed"
  mitigation: "<current mitigation measures>"
  residual_risk: 1–5
  remediation_due: "YYYY-MM-DD"
  related_controls: ["<control_id>"]
  evidence: ["<evidence_id>"]
```

---

## Governance Dashboard Metrics

| Metric | Target | Alert Threshold |
|---|---|---|
| Control implementation rate | ≥ 95% | < 85% |
| Evidence freshness (% controls with current evidence) | ≥ 90% | < 75% |
| Open Critical risks | 0 | ≥ 1 |
| Policy attestation current | 100% | < 100% |
| Audit readiness score | ≥ 85% | < 70% |
| Risk register reviewed (cadence) | Monthly | > 45 days since review |

---

## References

- `references/governance-reporting-template.md` — Dashboard format, risk register schema, policy attestation format
- `references/control-attestation.md` — Attestation workflow, sign-off requirements, evidence linking rules