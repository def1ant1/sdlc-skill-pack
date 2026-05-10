---
name: pii-detection
description: Applies multi-layer PII detection combining regex patterns, named entity recognition, and contextual classification to identify personal data across text, structured records, and documents with jurisdiction-aware categorization.
metadata:
  version: "1.0.0"
  category: privacy
  owner: privacy
  maturity: alpha
  dependencies: [privacy-runtime, data-fabric, telemetry]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Multi-layer PII detection engine for the enterprise privacy runtime. Identifies personal
and sensitive data across all content types — text, structured records, and documents —
using a three-layer detection approach that combines pattern matching, NER, and contextual
classification, with results categorized by PII type and applicable jurisdiction.

## Activation Triggers

- Content ingestion pipeline routes new documents for PII scanning before storage
- Data-redaction skill requests PII location map before redaction execution
- Residency-analysis skill requires PII identification for cross-boundary flow analysis
- Compliance audit requests a PII inventory of a specific dataset or document collection

## Execution Protocol

1. **Layer 1 — Pattern matching**: Apply jurisdiction-specific regex patterns for structured
   PII — email, phone, SSN, passport, credit card, IP address, date-of-birth — across all
   text content; record match location and type.

2. **Layer 2 — Named entity recognition**: Run NER model to identify person names, organization
   names, locations, and dates not captured by patterns; apply jurisdiction-specific sensitivity
   classifications.

3. **Layer 3 — Contextual classification**: Apply contextual analysis to identify sensitive
   data that requires context for identification — e.g., medical symptoms without a name still
   constitute health data when combined with other identifiers.

4. **Deduplicate and merge**: Consolidate overlapping detections; assign the highest-sensitivity
   category when multiple classifications apply to the same span.

5. **Classify by jurisdiction**: Tag each detected PII with applicable jurisdictions (GDPR,
   CCPA, HIPAA, PIPEDA) based on data subject geography and PII type.

6. **Emit PII map**: Return a structured PII location map with span offsets, PII types,
   sensitivity levels, and jurisdiction tags for downstream processing.

## Output Format

PII detection report with: `content_id`, `pii_instances` (list with span, type, sensitivity,
jurisdictions), `pii_type_summary` (counts by type), `highest_sensitivity_level`,
and `jurisdiction_flags` (applicable regulations).

## References

- `references/pii-taxonomy.md` — PII type definitions, regex pattern library, sensitivity levels, jurisdiction mapping