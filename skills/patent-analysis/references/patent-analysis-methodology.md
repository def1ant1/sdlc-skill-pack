# Patent Analysis Methodology Reference

## Patent Analysis Workflow

### Stage 1: Prior Art Search

```
Search protocol:
  1. Define search scope: IPC/CPC classification codes for target technology
  2. Construct keyword query:
     primary_keywords = [core_technology_terms]
     secondary_keywords = [synonyms, variant_spellings, related_terms]
     exclusion_terms = [clearly_unrelated_domains]

  3. Search sources (in priority order):
     a. USPTO Full-Text Patent Database
     b. EPO Espacenet
     c. Google Patents
     d. WIPO PATENTSCOPE
     e. NPL (Non-Patent Literature): ArXiv, ACM DL, IEEE Xplore

  4. Date range:
     prior_art_cutoff = priority_date_of_patent_under_analysis - 1 day
     search_range = [max(cutoff - 20 years, 1970), cutoff]

  5. Retrieve top-N by relevance (N ≥ 100 for freedom-to-operate; N ≥ 50 for patentability)
```

---

### Stage 2: Claim Parsing

Patent claims are the legally operative scope of a patent. Parse independently:

```yaml
claim_structure:
  patent_id: "US-10,234,567"
  claims:
    - claim_number: 1
      claim_type: "independent"
      preamble: "A system for processing natural language queries"
      body:
        - element: "a natural language processing module configured to receive a query"
          essential: true
        - element: "a knowledge graph comprising entity nodes and relation edges"
          essential: true
        - element: "wherein the processing module is further configured to
                    traverse the knowledge graph responsive to the query"
          essential: true
      scope: "broad"  # broad | medium | narrow

    - claim_number: 2
      claim_type: "dependent"
      depends_on: 1
      additional_limitation: "wherein entity nodes comprise at least five thousand entities"
      scope: "narrow"
```

**All-elements rule:** Infringement requires every element of an independent claim to be present in the accused product/process.

---

### Stage 3: Claim Chart Mapping

Map accused product/process features to claim elements:

```yaml
claim_chart:
  patent_id: "US-10,234,567"
  claim_number: 1
  accused_product: "Apotheon Semantic Layer v1.0"
  analysis_type: "literal"  # literal | doctrine_of_equivalents

  element_mapping:
    - element: "natural language processing module configured to receive a query"
      accused_feature: "semantic-layer skill's query parser (SKILL.md:L42-L58)"
      present: true
      notes: "Query parser accepts natural language via HTTP endpoint"

    - element: "knowledge graph comprising entity nodes and relation edges"
      accused_feature: "ontology/enterprise-ontology.md — 30+ entity types"
      present: true
      notes: "Entities and relations explicitly defined in ontology"

    - element: "traverse the knowledge graph responsive to the query"
      accused_feature: "semantic query execution engine"
      present: true
      notes: "Graph traversal is core mechanism"

  infringement_opinion: "HIGH_RISK"  # HIGH_RISK | MEDIUM_RISK | LOW_RISK | CLEAR
  confidence: 0.72
  caveats:
    - "Claim 1 element 3 may be distinguishable if traversal is indexed lookup vs. graph walk"
```

---

### Stage 4: Invalidity Analysis

A patent is invalid if prior art anticipates or renders it obvious:

```
ANTICIPATION (§102): All elements of the claim present in a single prior art reference.

  For each claim element e_i:
    FOR each prior art reference R:
      IF all {e_1, e_2, ..., e_n} present in R:
        FIND anticipation(R, claim)

OBVIOUSNESS (§103): Claim would have been obvious to person of ordinary skill
  combining multiple references.

  obviousness_analysis:
    primary_reference: R1  # Teaches most elements
    secondary_references: [R2, R3]  # Fill in missing elements
    motivation_to_combine: "Both solve the same problem in the same domain"
    teaching_away: "R1 does not teach away from R2's approach"
    conclusion: "Claim obvious over R1 in view of R2"
```

---

### Stage 5: FTO (Freedom-to-Operate) Opinion

```yaml
fto_opinion:
  product: "Apotheon Semantic Layer"
  opinion_date: "2026-05-07"
  jurisdiction: "United States"

  patents_analyzed: 24
  patents_high_risk: 2
  patents_medium_risk: 5
  patents_cleared: 17

  high_risk_patents:
    - patent_id: "US-10,234,567"
      owner: "Acme Corp"
      expiry_date: "2031-03-15"
      claim_chart_ref: "claim_chart_US10234567.yaml"
      recommended_action: "Design-around or license negotiation"
      design_around_options:
        - "Remove graph traversal; replace with indexed lookup"
        - "License from Acme Corp (estimated $50K/year)"

  overall_fto_assessment: "PROCEED_WITH_CAUTION"
  recommended_next_steps:
    - "Obtain formal legal opinion from qualified patent attorney"
    - "Explore design-around options for US-10,234,567"
    - "Monitor patent landscape for new filings in IPC class G06F-16/903"
```

---

## Patent Classification Reference

| IPC Class | Technology Domain |
|---|---|
| G06F-16 | Information retrieval, databases |
| G06N-3 | Neural networks, machine learning |
| G06N-20 | Machine learning (general) |
| G06F-40 | Natural language processing |
| G06Q-10 | Business process management |
| H04L-67 | Distributed computing, cloud |

---

## Analysis Confidence Thresholds

| Confidence | Meaning | Required Escalation |
|---|---|---|
| ≥ 0.85 | High confidence | No escalation required |
| 0.65–0.84 | Moderate confidence | Flag for attorney review |
| < 0.65 | Low confidence | Mandatory attorney review |
| Any HIGH_RISK | Regardless of confidence | Mandatory attorney review |