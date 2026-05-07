# Privacy Runtime PII Taxonomy

## Overview

Enterprise-level PII category hierarchy, sensitivity levels, jurisdiction obligations,
retention defaults, and deletion propagation requirements for the privacy-runtime.

---

## PII Category Hierarchy

```
Personal Information
├── L1 — Direct Identifiers (highest sensitivity)
│   ├── Government-issued identifiers (SSN, passport, national ID, driver's license)
│   ├── Financial account identifiers (bank account, credit card, IBAN, routing)
│   ├── Biometric data (fingerprint, facial recognition template, iris scan, voice print)
│   └── Unique persistent online identifiers (when linked to an individual)
├── L2 — Quasi-Identifiers (high sensitivity)
│   ├── Contact information (email, phone, physical address, IP address)
│   ├── Device identifiers (MAC address, IMEI, device serial, cookie ID)
│   └── Location data (GPS coordinates, precise location history)
├── L3 — Special Category / Sensitive Attributes (regulated)
│   ├── Health and medical data
│   ├── Genetic data
│   ├── Biometric data (processing for unique identification)
│   ├── Racial or ethnic origin
│   ├── Political opinions or affiliations
│   ├── Religious or philosophical beliefs
│   ├── Trade union membership
│   ├── Sexual orientation or gender identity
│   ├── Immigration status
│   ├── Mental health information
│   └── Criminal convictions or offenses
└── L4 — Contextual PII (moderate sensitivity)
    ├── Name (first name alone, when combined with context)
    ├── Age range or year of birth
    ├── General geographic area (city, postal code prefix)
    ├── Job title and employer
    └── Behavioral/preference data (when linked to an individual)
```

---

## Sensitivity Level → Jurisdiction Obligations

| Level | GDPR Basis Required | CCPA Category | HIPAA Classification | Processing Restrictions |
|---|---|---|---|---|
| L1 | Legal obligation or vital interest | Sensitive PI (financial) | PHI if health-linked | Minimize; encrypt at rest; access logging |
| L2 | Legitimate interest or contract | PI | PHI if health-linked | Encrypt in transit; audit access |
| L3 | Explicit consent or legal obligation | Sensitive PI | PHI | Strict access control; DPA notification for breaches |
| L4 | Legitimate interest | PI | N/A | Standard access control |

---

## Retention Defaults by Sensitivity Level

| Level | Default Retention Period | Deletion Trigger | Anonymization Permitted |
|---|---|---|---|
| L1 | Purpose + 30 days | Immediate on request (GDPR Art. 17) | No — must delete |
| L2 | Purpose + 90 days | Within 45 days of request | Pseudonymization only |
| L3 | Purpose + 30 days | Within 30 days of request (GDPR), 45 days (CCPA) | Aggregation ≥ 10 cohort |
| L4 | Purpose + 180 days | Within 45 days of request | Aggregation ≥ 5 cohort |

**"Purpose expiry"** is defined as the date when the processing purpose for which the
data was collected is concluded or the consent is withdrawn.

---

## Deletion Propagation Requirements

When a deletion request is received:

1. Identify all storage locations containing the data subject's records
2. Propagate deletion to all locations (primary, backup, archive, cache, logs)
3. For L1/L3 data: deletion must complete within 30 days; confirmation logged
4. For L2/L4 data: deletion must complete within 45 days; confirmation logged
5. Legal holds override deletion; conflicting holds must be resolved before deletion
6. Deletion audit record retained for 7 years (deletion itself must be auditable)

---

## Cross-Reference: PII Type → Detection Method

| PII Type | Sensitivity | Primary Detection | Jurisdiction Flag |
|---|---|---|---|
| SSN (US) | L1 | Regex: `\b\d{3}-\d{2}-\d{4}\b` | CCPA, HIPAA |
| Credit card | L1 | Regex (Luhn-validated) | PCI-DSS, CCPA |
| Passport number | L1 | Regex (country-specific) | GDPR, CCPA |
| Email | L2 | Regex | GDPR, CCPA, CASL |
| Phone | L2 | Regex (E.164) | GDPR, CCPA, TCPA |
| IP address | L2 | Regex (IPv4/IPv6) | GDPR (if linkable) |
| Health diagnosis | L3 | NER + Context (BERT) | HIPAA, GDPR Art. 9 |
| Racial origin | L3 | Context (LLM classifier) | GDPR Art. 9 |
| Religion | L3 | Context (LLM classifier) | GDPR Art. 9 |
| Full name | L4 | NER (PERSON entity) | GDPR, CCPA |
| City/region | L4 | NER (GPE entity) | GDPR (if combined) |

---

## Breach Notification Thresholds

| Data Sensitivity | Notification Required | Timeline | Notified Parties |
|---|---|---|---|
| L1 or L3 | Always | 72 hours (GDPR), without undue delay (CCPA) | DPA + affected individuals |
| L2 | If > 500 individuals affected | 72 hours (GDPR) | DPA; individuals if high risk |
| L4 | If > 1,000 individuals affected | Within 30 days (CCPA) | AG (CCPA); DPA if GDPR |