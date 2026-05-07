---
name: residency-analysis
description: Analyzes cross-boundary data flows to identify residency violations, maps compliant routing alternatives, and enforces data residency requirements before data is transferred across jurisdictional boundaries.
metadata:
  version: "1.0.0"
  category: privacy
  owner: privacy
  maturity: alpha
  dependencies: [privacy-runtime, pii-detection, data-fabric, telemetry]
---

## Role

Cross-boundary data flow analyzer and residency enforcement engine for the enterprise privacy
runtime. Evaluates proposed and active data flows against the residency requirements of all
applicable jurisdictions, blocks non-compliant transfers, and identifies compliant routing
alternatives that satisfy both technical and legal requirements.

## Activation Triggers

- Data pipeline proposes a cross-region data transfer requiring residency validation
- Federated-runtime receives a data request from a node in a different residency zone
- Pii-detection identifies data containing jurisdiction-specific personal information
- Compliance audit requests a residency analysis of current data flows

## Execution Protocol

1. **Identify data classification**: Retrieve the data classification (PII type, sensitivity,
   jurisdiction of data subjects) from pii-detection or the data fabric metadata.

2. **Map applicable residency rules**: For each data subject jurisdiction identified, retrieve
   the applicable residency requirements — data localization mandates (e.g., GDPR Article 46,
   Russia FZ-152), transfer restrictions, and approved transfer mechanisms (SCCs, BCRs, adequacy).

3. **Evaluate proposed flow**: Compare the source and destination of the proposed data flow
   against residency requirements; classify as COMPLIANT, NON-COMPLIANT, or CONDITIONALLY
   COMPLIANT (transfer mechanism required).

4. **Map compliant alternatives**: For NON-COMPLIANT flows, identify alternative architectures
   — local processing with aggregate export, federated query without data movement, or
   approved transfer mechanism application.

5. **Enforce or approve**: Block non-compliant transfers; for CONDITIONALLY COMPLIANT flows,
   verify the required transfer mechanism is in place before approving; log all decisions.

6. **Report residency status**: Emit a residency analysis report with flow classification,
   applicable rules, compliance status, and approved alternatives.

## Output Format

Residency analysis report with: `flow_id`, `source_region`, `destination_region`,
`data_classification`, `applicable_rules` (list with jurisdiction and requirement),
`compliance_status` (COMPLIANT/NON-COMPLIANT/CONDITIONAL), `transfer_mechanism_required`,
`compliant_alternatives` (list), and enforcement action taken.

## References

- `references/residency-rules.md` — jurisdiction residency requirements, transfer mechanism catalog, approved flow patterns