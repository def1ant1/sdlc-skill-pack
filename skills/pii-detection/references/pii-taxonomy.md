# PII Taxonomy Reference

## Overview

Defines all PII category types, their sensitivity levels, jurisdiction mappings,
detection methods, and retention defaults for the pii-detection skill.

---

## PII Category Hierarchy

### Level 1: Direct Identifiers (L1 — Highest Sensitivity)

These directly identify a natural person without additional data.

| PII Type | Examples | Primary Detection Method |
|---|---|---|
| Full legal name | "John Michael Smith" | NER (PERSON) |
| Government ID | SSN, passport number, national ID | Regex |
| Financial account | Bank account, credit card, IBAN | Regex |
| Biometric identifier | Fingerprint hash, facial embedding ID | Pattern + context |
| Exact date of birth | "1985-03-15" | Regex + context |

### Level 2: Quasi-Identifiers (L2 — High Sensitivity)

These can identify a person when combined with other data.

| PII Type | Examples | Primary Detection Method |
|---|---|---|
| Email address | user@domain.com | Regex |
| Phone number | +1-555-867-5309 | Regex |
| Physical address | "123 Main St, Springfield" | NER (GPE) + Regex |
| IP address | 192.168.1.1, 2001:db8::1 | Regex |
| Device identifier | MAC address, IMEI, device UUID | Regex |
| Vehicle identifier | License plate, VIN | Regex |

### Level 3: Sensitive Attributes (L3 — Sensitive)

These reveal sensitive personal characteristics protected by law.

| PII Type | Jurisdiction Sensitivity | Detection Method |
|---|---|---|
| Health/medical data | HIPAA, GDPR Art. 9 | Context + NER |
| Racial or ethnic origin | GDPR Art. 9, CCPA | Context + NER |
| Religious beliefs | GDPR Art. 9 | Context |
| Political opinions | GDPR Art. 9 | Context |
| Sexual orientation/gender identity | GDPR Art. 9, various | Context |
| Immigration status | CCPA, various | Context + NER |
| Mental health information | HIPAA, GDPR Art. 9 | Context + NER |
| Criminal record | Various | Context + NER |

### Level 4: Contextual PII (L4 — Moderate Sensitivity)

These become PII only in context of the surrounding data.

| PII Type | Examples | Detection Method |
|---|---|---|
| First name only | "Jennifer" | NER (when near other PII) |
| Job title + employer | "VP of Sales at Acme Corp" | NER + context |
| Age range | "mid-40s" | Context (when combined with other data) |
| General location | "Brooklyn, NY" | NER (GPE) |
| Workplace | "works at General Hospital" | Context |

---

## Jurisdiction Mapping

| PII Category | GDPR | CCPA | HIPAA | PIPEDA |
|---|---|---|---|---|
| L1 — Direct identifiers | Personal data | PI | PHI (if health-related) | PI |
| L2 — Quasi-identifiers | Personal data | PI | PHI (if health-related) | PI |
| L3 — Health data | Special category | Sensitive PI | PHI | Sensitive PI |
| L3 — Other sensitive attrs | Special category | Sensitive PI | N/A | Sensitive PI |
| L4 — Contextual | Personal data (in context) | PI (in context) | N/A | PI (in context) |

---

## Regex Pattern Library (Selected)

```python
# US Social Security Number
r'\b(?!000|666|9\d{2})\d{3}[- ]\d{2}[- ]\d{4}\b'

# Credit card numbers (Visa, MC, Amex, Discover)
r'\b(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11})\b'

# Email address
r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# US phone number
r'\b(?:\+1[-.\s]?)?\(?[0-9]{3}\)?[-.\s][0-9]{3}[-.\s][0-9]{4}\b'

# IPv4
r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

# US passport
r'\b[A-Z][0-9]{8}\b'

# IBAN
r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b'

# Date of birth patterns
r'\b(?:born|dob|date of birth|birthday)[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
```

---

## Detection Layer Assignment

| PII Type | Layer 1 (Regex) | Layer 2 (NER) | Layer 3 (Context) |
|---|---|---|---|
| SSN, passport, card numbers | PRIMARY | Backup | N/A |
| Email, phone, IP | PRIMARY | Backup | N/A |
| Full name | Secondary | PRIMARY | Verification |
| Address | Secondary | PRIMARY | Verification |
| Health data | N/A | Supporting | PRIMARY |
| Religious/political views | N/A | Supporting | PRIMARY |
| Sexual orientation | N/A | N/A | PRIMARY |

---

## Sensitivity Level → Retention Defaults

| Level | Default Retention | Deletion on Request | Anonymization Option |
|---|---|---|---|
| L1 | 90 days after purpose expires | Required within 30 days | Pseudonymization only |
| L2 | 180 days after purpose expires | Required within 30 days | Pseudonymization allowed |
| L3 | 365 days after purpose expires | Required within 30 days | Aggregation to cohort ≥ 5 |
| L4 | 365 days after purpose expires | Required within 60 days | Aggregation allowed |