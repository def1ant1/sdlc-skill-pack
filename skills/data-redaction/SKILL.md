---
name: data-redaction
description: Executes jurisdiction-aware PII redaction, pseudonymization, and tokenization on identified personal data, maintaining referential integrity across related records while producing audit-traceable redaction logs.
metadata:
  version: "1.0.0"
  category: privacy
  owner: privacy
  maturity: alpha
  dependencies: [privacy-runtime, pii-detection, data-fabric, telemetry]
---

## Role

Jurisdiction-aware data redaction and pseudonymization engine for the enterprise privacy
runtime. Transforms personal data identified by pii-detection into privacy-preserving
representations — redaction, pseudonymization, or tokenization — selected based on the
applicable jurisdiction requirements and the downstream use case for the data.

## Activation Triggers

- Pii-detection emits a PII map for a content item requiring privacy transformation
- Legal-hold-management releases a hold and triggers redaction of previously preserved data
- Residency-analysis identifies cross-boundary data requiring local redaction before transfer
- Operator initiates a GDPR erasure request requiring targeted redaction

## Execution Protocol

1. **Load PII map and redaction policy**: Retrieve the PII location map from pii-detection
   and the applicable redaction policy for each jurisdiction and PII type combination.

2. **Select transformation method**: For each PII instance, select the appropriate method —
   REDACT (replace with [REDACTED] or type tag), PSEUDONYMIZE (replace with consistent
   pseudonym, mapping stored in secure vault), or TOKENIZE (replace with reversible token
   for analytics use cases).

3. **Apply transformations**: Execute transformations on the content; for pseudonymization,
   ensure consistent mapping (same PII value always maps to the same pseudonym within a scope).

4. **Maintain referential integrity**: Where PII spans multiple related records (e.g., name
   in a transaction linked to a customer record), apply consistent pseudonyms across all records.

5. **Verify completeness**: Re-scan transformed content with pii-detection to verify no PII
   instances were missed; flag any residual PII for manual review.

6. **Log redaction record**: Write an audit-traceable redaction log with content ID, PII
   types redacted, methods applied, and operator/trigger identity.

## Output Format

Redaction record with: `content_id`, `pii_instances_processed` (count), `methods_applied`
(breakdown by type), `pseudonym_scope_id` (if applicable), `referential_integrity_check`
(PASS/FAIL), and `redaction_audit_log_id`.

## References

- `references/redaction-policy.md` — jurisdiction-method mapping table, pseudonymization scope rules, reversibility conditions