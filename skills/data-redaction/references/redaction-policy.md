# Redaction Policy Reference

## Jurisdiction-Method Mapping Table

For each jurisdiction and PII sensitivity level combination, this table specifies the
required or recommended redaction method:

| Jurisdiction | PII Sensitivity | Required Method | Reversibility |
|---|---|---|---|
| EU (GDPR) — Art. 17 erasure request | L1 | Irreversible deletion | Irreversible |
| EU (GDPR) — analytics use | L1, L2 | Pseudonymization | Reversible (with key) |
| EU (GDPR) — research publication | L1, L2, L3 | Anonymization (k≥5) | Irreversible |
| US HIPAA — treatment context | L1, L3 (health) | De-identification (Safe Harbor or Expert Determination) | Irreversible |
| US HIPAA — research | L3 (health) | Expert determination + limited dataset | Conditional |
| US CCPA — deletion request | L1, L2 | Irreversible deletion | Irreversible |
| China PIPL — cross-border transfer | All | Pseudonymization (key stays in CN) | Reversible (with key in CN) |
| Russia FZ-152 — cross-border | All | Pseudonymization (key stays in RU) | Reversible (with key in RU) |
| Internal analytics (no legal basis) | L4 | Aggregation (cohort ≥ 5) | Irreversible |
| Audit logs (long retention) | L2 | Tokenization | Reversible (with vault access) |

---

## Redaction Method Definitions

### REDACT (Literal Replacement)

Replace the PII span with a type indicator or uniform placeholder:

```
Original:  "Patient Jane Smith (DOB: 1985-03-15) presented with..."
Redacted:  "Patient [PERSON] (DOB: [DATE]) presented with..."
```

- **Use for:** Output to external parties, public reports, AI training data
- **Reversibility:** Irreversible
- **PII recovery:** Not possible

### PSEUDONYMIZE (Consistent Alias)

Replace the PII span with a consistent pseudonym derived from a keyed hash.
The same PII value always maps to the same pseudonym within a scope.

```
Original:  "Jane Smith's account (account: AC-12345) shows..."
Pseudo:    "Customer-A7F2B's account (account: AC-XXXXXX) shows..."
```

- **Pseudonym format:** `[EntityType]-[6-char hash]` (e.g., `Customer-A7F2B`)
- **Key storage:** Pseudonymization keys stored in the secure vault; access-controlled
- **Scope:** Pseudonym consistency guaranteed within a defined scope (e.g., workflow, project)
- **Use for:** Analytics that require tracking across records without identifying individuals
- **Reversibility:** Reversible with vault key access (authorized by privacy officer)

### TOKENIZE (Reversible Token)

Replace PII with an opaque token that can be reversed by authorized systems.

```
Original:  "SSN: 123-45-6789"
Tokenized: "SSN: TKN-8F3A2C1B9D"
```

- **Token storage:** Token-to-value mapping stored in tokenization vault
- **Use for:** Systems that need to join on PII later (e.g., reconciliation workflows)
- **Reversibility:** Fully reversible by systems with vault access
- **Audit:** Every detokenization request is logged with requester identity

### ANONYMIZE (Irreversible Generalization)

Generalize or suppress PII to prevent re-identification. k-anonymity requires at least
k=5 individuals to share every combination of quasi-identifier values.

```
Original:  DOB: 1985-03-15, ZIP: 90210
Anonymized: Age range: 35-44, Region: Southern California
```

- **Use for:** Research datasets, published statistics
- **Reversibility:** Irreversible
- **Standard:** k-anonymity (k≥5) + l-diversity (≥3 sensitive attribute values per group)

---

## Pseudonymization Scope Rules

Scope determines within which boundary a pseudonym is consistent:

| Scope | Definition | When to Use |
|---|---|---|
| `workflow` | Same pseudonym within a single workflow execution | Short-lived analytics |
| `project` | Same pseudonym across all workflows in a project | Multi-workflow reconciliation |
| `organization` | Same pseudonym across all workflows organization-wide | Enterprise-wide analytics |
| `global` | Same pseudonym across all scopes (maximum consistency) | Long-term customer tracking |

**Scope selection rule:** Use the narrowest scope that satisfies the use case.
Broader scopes increase the risk of re-identification through pseudonym correlation.

---

## Reversibility Conditions

Detokenization or de-pseudonymization is permitted only when:

1. **Authorization:** Request is from a system or person with explicit vault access grant
2. **Purpose limitation:** The stated purpose for detokenization matches the original purpose
   for which the data was collected
3. **Legal basis:** A valid legal basis exists (consent, legal obligation, vital interests)
4. **Audit trail:** The detokenization request is logged with requester, timestamp, purpose,
   and which records were accessed
5. **Not after erasure:** Pseudonymized data cannot be detokenized after the data subject
   has submitted a valid erasure request

---

## Redaction Completeness Verification

After applying redactions, the privacy-runtime re-scans the output with pii-detection
using a lower confidence threshold (0.5 instead of the normal 0.7) to catch any
residual PII. Residual PII found after redaction is escalated for manual review.

**Acceptable residual PII rate:** < 0.1% of records (i.e., ≥ 99.9% redaction effectiveness)