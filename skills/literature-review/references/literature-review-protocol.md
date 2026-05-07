# Literature Review Protocol

## Search Strategy Frameworks

### PICO Framework (Clinical / Quantitative Research)

| Element | Definition | Example |
|---|---|---|
| P — Population | Who is being studied? | Enterprise AI agents |
| I — Intervention | What is being tested? | Constitutional AI alignment methods |
| C — Comparison | What is the control/comparison? | Standard RLHF fine-tuning |
| O — Outcome | What is the measured result? | Alignment score, deception rate |

**Boolean query construction:**
```
("constitutional AI" OR "AI alignment" OR "value alignment") AND
("enterprise" OR "autonomous agent" OR "agentic system") AND
("evaluation" OR "benchmark" OR "safety score")
```

### SPIDER Framework (Qualitative / Mixed Methods Research)

| Element | Definition |
|---|---|
| S — Sample | Population being studied |
| PI — Phenomenon of Interest | Concept or experience under study |
| D — Design | Study design type |
| E — Evaluation | Outcome or measure |
| R — Research type | Qualitative / quantitative / mixed |

---

## Search Source Tiers

Search sources are prioritized in three tiers:

| Tier | Sources | Inclusion Rationale |
|---|---|---|
| 1 (Primary) | arXiv, ACL Anthology, NeurIPS, ICML, ICLR proceedings | Highest technical quality for AI research |
| 2 (Secondary) | Google Scholar, Semantic Scholar, SSRN, IEEE Xplore | Broad coverage; cross-domain |
| 3 (Internal) | Enterprise knowledge graph, internal research repository | Organizational context |

**Minimum:** Search ≥ 2 Tier 1 sources and ≥ 1 Tier 2 source. Document all search
strings and result counts per source for reproducibility.

---

## PRISMA-Compliant Screening Protocol

### Stage 1: Identification

- Record all search results per source (including duplicates)
- Deduplicate across sources using DOI or title+author matching
- Document: total records identified, duplicates removed

### Stage 2: Screening (Title + Abstract)

Apply inclusion/exclusion criteria to title and abstract only:

**Standard inclusion criteria:**
- Published within the defined date range
- Available in English (or available with translation)
- Reports empirical findings or theoretical contribution relevant to the research question

**Standard exclusion criteria:**
- Conference workshop papers with no peer review indication (unless from top venues)
- Papers where full text is unavailable
- Editorials, commentaries, and opinion pieces (unless specifically relevant)

Document: records screened, records excluded (with reason)

### Stage 3: Eligibility (Full Text)

Apply more detailed inclusion/exclusion to full text:

- Verify the study design matches the research question requirements
- Check that outcome measures align with the research question
- Apply quality assessment (see Evidence Grading below)

Document: full-text articles assessed, articles excluded (with specific reason)

### Stage 4: Included

- Final set of included studies for evidence extraction
- Document: studies included in synthesis

---

## Evidence Grading Schema (Levels I–V)

| Level | Study Design | Reliability |
|---|---|---|
| I | Systematic review / meta-analysis of RCTs | Highest |
| II | Well-designed RCT with adequate power | High |
| III | Quasi-experimental (DiD, IV, RD) or cohort study | Moderate |
| IV | Cross-sectional survey, case-control, or observational | Low-moderate |
| V | Expert opinion, case report, theoretical analysis | Lowest |

**Quality modifiers (upgrade or downgrade level):**
- +1 level: Large effect size, dose-response relationship, or multiple independent replications
- -1 level: High risk of bias (selection bias, measurement bias), significant limitations
- -1 level: Short follow-up, small sample, or non-representative population

---

## Conflict Resolution Rules

When included studies have conflicting findings:

1. **Document the conflict** — note the specific disagreement and the studies involved
2. **Assess study quality** — higher-quality studies (lower Level number) take precedence
3. **Check for moderators** — conflicting results may be explained by population, context, or measurement differences
4. **Apply weight of evidence** — if multiple Level III studies conflict with one Level II study, weight the Level II study more heavily but acknowledge the inconsistency
5. **Flag as inconclusive** — if high-quality studies remain in genuine conflict, classify the evidence for that question as "insufficient/conflicting" and identify as a research gap

---

## Search Protocol Record (Reproducibility)

```yaml
search_protocol:
  research_question: "string (PICO/SPIDER formatted)"
  search_date: "ISO8601"
  date_range: "YYYY to YYYY"
  languages: [English]

  searches:
    - source: "arXiv (cs.AI, cs.LG)"
      query_string: "string"
      results_retrieved: N
      date_searched: "ISO8601"
    - source: "Semantic Scholar"
      query_string: "string"
      results_retrieved: N
      date_searched: "ISO8601"

  screening:
    total_identified: N
    duplicates_removed: N
    screened: N
    excluded_screening: N
    full_text_assessed: N
    excluded_full_text: N
    included: N

  inclusion_criteria: [list]
  exclusion_criteria: [list]
```