# Contract Templates

## Template Registry

| Template | Use Case | Auto-Generate | Legal Review |
|---|---|---|---|
| `mutual-nda` | Both parties share confidential info | Yes | Required before signing |
| `one-way-nda` | Only counterparty receives confidential info | Yes | Required before signing |
| `msa-standard` | Master service agreement (standard terms) | Partial | Required before signing |
| `sow-template` | Statement of work under an MSA | Yes | L2 review |
| `dpa-standard` | Data processing agreement for GDPR | Yes | Required before signing |
| `offer-letter` | Employment offer letter | Yes | HR + L2 review |
| `contractor-agreement` | Independent contractor agreement | Yes | L2 review |

---

## Mutual NDA Template

```
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of [DATE]
by and between:

Apotheon.ai, Inc. ("Company"), a [State] corporation, and
[COUNTERPARTY NAME] ("[SHORT NAME]"), a [entity type].

(Each a "Party," collectively the "Parties.")

1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means any non-public information disclosed by
   either Party to the other, either directly or indirectly, in writing, orally,
   or by inspection of tangible objects, that is designated as "Confidential"
   or that reasonably should be understood to be confidential.

   Confidential Information does not include information that: (a) is or becomes
   generally publicly known through no fault of the receiving Party; (b) was
   rightfully known to the receiving Party prior to disclosure; (c) is rightfully
   obtained by the receiving Party from a third party without restriction; or
   (d) was independently developed by the receiving Party without use of the
   disclosing Party's Confidential Information.

2. OBLIGATIONS
   Each Party agrees to: (a) hold the other Party's Confidential Information in
   strict confidence; (b) use the Confidential Information only for the purpose
   of evaluating a potential business relationship between the Parties ("Purpose");
   (c) not disclose the Confidential Information to any third party except employees,
   agents, or advisors who need to know it for the Purpose and who are bound by
   confidentiality obligations at least as protective as this Agreement.

3. TERM
   This Agreement is effective as of the date above and will remain in effect for
   [2] years. Obligations with respect to Confidential Information received during
   the term will survive for [3] years following disclosure.

4. RETURN OF INFORMATION
   Upon request by the disclosing Party, the receiving Party will promptly return
   or destroy all Confidential Information and certify such destruction in writing.

5. GOVERNING LAW
   This Agreement is governed by the laws of [State], without regard to conflict
   of law principles.

6. ENTIRE AGREEMENT
   This Agreement constitutes the entire agreement between the Parties with respect
   to the subject matter hereof and supersedes all prior discussions and agreements.

COMPANY:                              [COUNTERPARTY]:
Apotheon.ai, Inc.                     [COUNTERPARTY NAME]

By: _______________________           By: _______________________
Name: _____________________           Name: _____________________
Title: ____________________           Title: ____________________
Date: _____________________           Date: _____________________
```

---

## DPA Template (GDPR)

Key provisions that must be present in every Data Processing Agreement:

1. **Subject matter and duration** of the processing
2. **Nature and purpose** of the processing
3. **Type of personal data** and categories of data subjects
4. **Obligations and rights of the controller**
5. **Processor obligations**: process only on controller's instructions; confidentiality; security measures; sub-processor restrictions; data subject rights assistance; deletion on termination; audit cooperation
6. **Sub-processors**: list of approved sub-processors; notification of changes
7. **International transfers**: SCCs or equivalent if data leaves EU
8. **Security measures**: description of technical and organizational measures (Article 32)

---

## Standard Position Table (Non-Negotiable)

These positions must appear in all vendor agreements:

| Clause | Apotheon Position | Will Accept |
|---|---|---|
| Governing law | Company home state | Neutral state |
| Liability cap | 12 months of fees | Not less than 6 months |
| Indemnification | Mutual | Will not accept one-sided against Company |
| IP ownership | Company owns all work product | No exceptions |
| Auto-renewal notice | 30 days | Up to 60 days; not more |
| Termination for convenience | 30 days notice | Up to 60 days |
| Data processing | DPA required for PII | Non-negotiable |