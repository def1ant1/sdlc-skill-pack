# Data Residency Rules Reference

## Jurisdiction Residency Requirements

### European Union — GDPR (Regulation 2016/679)

**Applicable to:** Personal data of EU/EEA residents

**Requirements:**
- No absolute localization mandate — processing outside EU/EEA is permitted with proper mechanism
- Cross-border transfer requires one of the approved mechanisms (Articles 44–49)
- Special category data (Art. 9) requires explicit consent or legal basis plus transfer mechanism

**Approved transfer mechanisms:**
| Mechanism | Legal Basis | Documentation Required |
|---|---|---|
| Adequacy Decision | European Commission determination | No additional docs needed |
| Standard Contractual Clauses (SCCs 2021) | Art. 46(2)(c) | Executed SCC modules 1–4 |
| Binding Corporate Rules | Art. 47 | BCR approved by lead DPA |
| Derogations (consent) | Art. 49(1)(a) | Explicit consent record per transfer |
| Derogations (contractual necessity) | Art. 49(1)(b) | Contract reference |

**Current adequacy decisions (selected):** Andorra, Canada (commercial), Israel, Japan, New Zealand, South Korea, Switzerland, UK, Uruguay, US (DPF-certified entities only)

---

### Russia — Federal Law No. 152-FZ (Personal Data)

**Applicable to:** Personal data of Russian citizens

**Requirements:**
- **Mandatory localization:** Initial collection and storage of Russian citizens' personal data must occur on servers located in Russia
- Cross-border transfer is permitted AFTER Russian storage is established
- Operators must maintain a cross-border transfer database
- Roskomnadzor registration required for operators of significant scale

**Implementation rule:** Data tagged `jurisdiction: RU` must land on a `region: ru-*` node within
the same transaction before any processing on non-Russian nodes. Cross-border copies are
permitted; the Russian primary record must remain.

---

### China — Personal Information Protection Law (PIPL, 2021)

**Applicable to:** Personal information of individuals within China

**Requirements:**
- **Critical Information Infrastructure Operators (CIIO):** Must store PI and Important Data within China
- **Non-CIIO:** Must comply with CAC security assessment or standard contract for cross-border transfer
- Sensitive PI requires separate notice and consent
- Transfer recipients in countries with "adequate protection" may use simplified mechanism

**Approved mechanisms:**
| Mechanism | Who It Applies To | Requirements |
|---|---|---|
| CAC Security Assessment | CIIO or large-scale data processors | Submit assessment; 2-year validity |
| Standard Contract | Non-CIIO | CAC-registered standard contract |
| Certification | Non-CIIO | Approved certification body |

**CAC Assessment Threshold:** Required if transferring > 100,000 individuals' PI per year, or
> 10,000 individuals' sensitive PI per year.

---

### United States — State and Federal Laws

| Law | Jurisdiction | Localization Requirement | Key Restrictions |
|---|---|---|---|
| CCPA/CPRA | California residents | None | Consumer rights (deletion, portability) must be implementable across all locations |
| HIPAA | Healthcare PHI | None | BAA required with all data processors; encryption mandatory |
| COPPA | Children < 13 | None | Parental consent; FTC breach notification |
| GLBA | Financial data | None | Safeguards rule; breach notification |
| State biometric laws (IL, TX, WA) | Biometric data | None | Consent; retention limits; destruction |

---

## Transfer Mechanism Catalog

```yaml
transfer_mechanisms:
  - id: "EU-ADEQUACY"
    name: "EU Adequacy Decision"
    applicable_jurisdictions: [EU, EEA]
    destination_scope: "Countries with active adequacy decision"
    documentation: "Country list reference only"
    renewal_required: false

  - id: "EU-SCC-C2C"
    name: "EU SCCs — Controller to Controller (Module 1)"
    applicable_jurisdictions: [EU, EEA]
    destination_scope: "Any country"
    documentation: "Executed Module 1 SCC"
    renewal_required: false  # Unless transfer assessment triggers review

  - id: "EU-SCC-C2P"
    name: "EU SCCs — Controller to Processor (Module 2)"
    applicable_jurisdictions: [EU, EEA]
    destination_scope: "Any country"
    documentation: "Executed Module 2 SCC + transfer impact assessment (TIA)"
    renewal_required: false

  - id: "CN-CAC-ASSESSMENT"
    name: "China CAC Security Assessment"
    applicable_jurisdictions: [CN]
    destination_scope: "Any country"
    documentation: "CAC approval reference number"
    renewal_required: true
    renewal_period_years: 2

  - id: "CN-STANDARD-CONTRACT"
    name: "China PIPL Standard Contract"
    applicable_jurisdictions: [CN]
    destination_scope: "Any country"
    documentation: "Executed standard contract; filed with CAC"
    renewal_required: false
```

---

## Approved Cross-Boundary Flow Patterns

These patterns are pre-approved as compliant without per-transfer review:

| Pattern | Description | Compliance Basis |
|---|---|---|
| Local processing + aggregate export | Raw PI stays in origin; only cohort statistics (≥ 5) cross boundary | Aggregate is not personal data |
| Federated query | Compute moves to data; only query results (non-personal) return | No personal data crosses |
| Irreversible anonymization before transfer | k-anonymity (k≥5) or differential privacy applied | Anonymized data is not personal data |
| Pseudonymization with origin key | Data pseudonymized; key retained in origin jurisdiction | Transfer of pseudonymized data |
| Intra-group BCR transfer | Transfer within the corporate group under approved BCR | BCR covers all intra-group transfers |

---

## Compliance Status Flow

```
PROPOSED FLOW → residency-analysis skill
    → COMPLIANT: Approve transfer; log decision
    → NON-COMPLIANT: Block transfer; notify operator
    → CONDITIONAL: Verify transfer mechanism documentation;
                   if mechanism confirmed → COMPLIANT
                   if mechanism missing → NON-COMPLIANT
```