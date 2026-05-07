---
name: privacy-runtime
description: Enterprise privacy enforcement runtime that detects and redacts PII, enforces data retention policies, manages legal holds, and ensures data residency compliance across all workflows.
metadata:
  version: "1.0.0"
  category: security
  owner: platform
  maturity: alpha
  dependencies: [governance, data-fabric, alignment-engine, telemetry]
---

## Role

Privacy and data protection runtime for the enterprise OS. Intercepts data flows containing
PII, enforces retention schedules, applies legal holds, and ensures data residency compliance —
providing a continuous privacy enforcement layer woven into all skills and workflows.

## Activation Triggers

- Data containing PII detected passing through a workflow
- Retention policy evaluation schedule triggered (daily)
- Legal hold order received or released
- Cross-border data transfer attempted
- Privacy compliance audit or DSAR (data subject access request) initiated

## Execution Protocol

1. **Intercept data flow**: Monitor data payloads passing through workflow steps; extract
   content for PII scanning when data classification indicates potential sensitivity.

2. **Detect PII**: Invoke pii-detection skill to scan for PII categories; collect detection
   results with category, location, and confidence score.

3. **Apply redaction or masking**: Invoke data-redaction with appropriate strategy (full
   redaction, pseudonymization, tokenization) based on purpose, consumer, and jurisdiction.

4. **Enforce retention**: Check data age against retention schedule; trigger deletion workflow
   or archive transition for data exceeding retention period.

5. **Apply legal hold**: Flag held data records; block deletion regardless of retention schedule
   until hold is released by authorized legal-ops owner.

6. **Enforce residency**: Check cross-boundary transfers against residency-analysis constraints;
   block prohibited transfers; route to compliant alternative if available.

## Output Format

Privacy enforcement action log with: PII detected and redacted, retention actions taken, hold
status updates, and residency compliance check outcomes per data flow.

## References

- `references/pii-taxonomy.md` — PII category definitions, detection patterns, redaction rules by data type and jurisdiction