# Residency Enforcement Rules

## Overview

Jurisdiction residency requirements, enforcement mechanisms, approved cross-boundary data
patterns, and air-gapped deployment requirements for the federated-runtime.

---

## Jurisdiction Residency Requirements

### European Union — GDPR (Articles 44–49)

| Requirement | Rule |
|---|---|
| Data localization | Personal data of EU residents must be processed within EU/EEA by default |
| Cross-border transfer | Permitted only with an approved transfer mechanism |
| Approved mechanisms | Adequacy decision, Standard Contractual Clauses (SCCs), Binding Corporate Rules (BCRs), explicit consent |
| Prohibited destinations | Countries without adequacy decision and no fallback mechanism |
| Special category data | GDPR Art. 9 data (health, biometric, etc.) requires heightened justification |

**Implementation:** All data tagged with `jurisdiction: EU` must be processed on nodes
in `region: eu-*` or nodes explicitly listed in an approved BCR or SCC.

---

### Russia — Federal Law No. 152-FZ

| Requirement | Rule |
|---|---|
| Data localization | Personal data of Russian citizens must be initially collected and stored within Russia |
| Cross-border transfer | Permitted after Russian storage; transfer database must be maintained |
| Prohibited categories | Certain financial and biometric data requires additional Roskomnadzor notification |
| Penalties | Roskomnadzor may block access to services in violation |

**Implementation:** Data tagged with `jurisdiction: RU` must first land on `region: ru-*` nodes.
Transfer copies may exist on other nodes if Russian primary is maintained.

---

### China — Personal Information Protection Law (PIPL, Articles 38–43)

| Requirement | Rule |
|---|---|
| Data localization | PI of Chinese residents processed by Critical Information Infrastructure operators must stay in China |
| Cross-border transfer | Requires CAC security assessment OR standard contract OR certification |
| Sensitive PI | Additional consent and separate notice required |
| Transfer restrictions | Cannot transfer to countries that CAC determines have insufficient protection |

**Implementation:** Data tagged with `jurisdiction: CN` requires `region: cn-*` placement
plus explicit CAC assessment record for any cross-border transfer.

---

### United States — CCPA / CPRA (California)

| Requirement | Rule |
|---|---|
| Data localization | No mandatory localization requirement |
| Cross-border transfer | No prohibition; contractual safeguards recommended |
| Sensitive PI | Heightened disclosure and opt-out rights for sensitive categories |
| Consumer rights | Deletion and portability rights must be technically implementable |

**Implementation:** CCPA data has no localization constraint but must support deletion
propagation within 45 days of request across all storage locations.

---

## Approved Cross-Boundary Transfer Mechanisms

| Mechanism | Jurisdictions | Requirements | Documentation |
|---|---|---|---|
| EU Adequacy Decision | EU → Adequate country | None beyond identification | Country list maintained by European Commission |
| SCCs (2021) | EU → Any country | Executed SCC agreement | Document reference in data contract |
| BCRs | EU → Intra-group | BCR approved by lead DPA | BCR approval reference |
| Consent | EU → Any country | Explicit, informed, specific consent | Consent record ID |
| Contractual necessity | EU → Any country | Contract with data subject | Contract reference |
| China SCC | CN → Any country | CAC-registered standard contract | Registration confirmation |
| CAC Security Assessment | CN → Restricted countries | CAC approval | Assessment approval ID |

---

## Air-Gapped Deployment Requirements

For deployments in air-gapped environments (no external network connectivity):

| Requirement | Specification |
|---|---|
| Model weights | Pre-loaded; no runtime download permitted |
| Updates | Offline update package; cryptographically signed by vendor |
| Telemetry | Stored locally; exported via approved offline channel (air-gap transfer) |
| Secret management | Local key management system; no cloud KMS |
| Audit logs | Local immutable storage; export via physical media or approved air-gap link |
| External API calls | All external integrations must be mocked or disabled |

**Verification:** Air-gapped compliance is verified at startup by the federated-runtime
health check. Any external network connection attempt by an agent triggers immediate
alert and agent suspension.

---

## Enforcement Mechanisms

| Enforcement Level | Mechanism | Action |
|---|---|---|
| Pre-transfer gate | residency-analysis skill check before any data transfer | Block non-compliant transfers |
| Runtime monitoring | Network egress filter on agent-kernel | Drop packets to prohibited destinations |
| Post-hoc audit | Lineage analysis cross-checks transfer logs | Flag violations for compliance team |
| Operator alert | Any enforcement action triggers operator notification | Immediate alert with flow details |

---

## Approved Cross-Boundary Flow Patterns

These architectural patterns are pre-approved as compliant without per-transfer review:

1. **Local processing, aggregate export:** Raw personal data stays in origin region;
   only statistical aggregates (cohort size ≥ 5) cross the boundary.

2. **Federated query:** Compute moves to data; only query results (non-personal) cross the boundary.

3. **Anonymized transfer:** Data is irreversibly anonymized before transfer; no personal
   data crosses the boundary.

4. **Pseudonymized transfer with key residency:** Data is pseudonymized with the key
   remaining in the origin jurisdiction; pseudonymized data may cross boundary.