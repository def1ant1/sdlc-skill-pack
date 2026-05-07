# Decision Criteria

## Standard Criteria Sets by Decision Type

### Technology / Build vs Buy

| Criterion | Weight | Description |
|---|---|---|
| Strategic fit | 25% | Does this align with our core differentiation? |
| Total cost of ownership | 20% | 3-year cost (build, maintain, operate) |
| Time to value | 20% | How quickly can we deliver value? |
| Risk | 15% | Technical, vendor, security risks |
| Flexibility | 10% | Can we adapt as requirements change? |
| Team capability | 10% | Do we have the skills to succeed? |

### Vendor / Supplier Selection

| Criterion | Weight | Description |
|---|---|---|
| Capability fit | 30% | Does the vendor meet the functional requirements? |
| Total cost | 25% | Price + implementation + ongoing cost |
| Security & compliance | 20% | SOC 2, GDPR, data handling |
| Support & reliability | 15% | SLAs, support responsiveness, uptime track record |
| Strategic alignment | 10% | Vendor roadmap aligns with our direction |

### Feature Prioritization

| Criterion | Weight | Description |
|---|---|---|
| User impact | 30% | Number of users affected × severity |
| Revenue impact | 25% | Direct revenue effect or retention value |
| Strategic importance | 20% | Alignment with OKRs and product vision |
| Implementation effort | 15% | Inverse of effort (lower effort = higher score) |
| Risk | 10% | Technical and business risk of implementing |

### Hiring / Team Investment

| Criterion | Weight | Description |
|---|---|---|
| Capability gap | 30% | How critical is this skill gap? |
| Business impact | 25% | What does filling this role unlock? |
| Market availability | 20% | How hard is this role to fill? |
| Cost vs value | 15% | Fully-loaded cost vs expected contribution |
| Timing | 10% | Is now the right time? |

### Architecture Decisions

| Criterion | Weight | Description |
|---|---|---|
| Correctness | 25% | Does this approach correctly solve the problem? |
| Operational simplicity | 20% | How easy is this to operate at scale? |
| Cost | 20% | Infrastructure and maintenance cost |
| Reversibility | 15% | How easy is this to change later? |
| Security | 10% | Does this introduce security risks? |
| Familiarity | 10% | Team experience with this approach |

---

## Scoring Scale

All criteria are scored 1–5:

| Score | Meaning |
|---|---|
| 5 | Excellent — exceeds requirements or expectations |
| 4 | Good — meets requirements with room to spare |
| 3 | Adequate — meets minimum requirements |
| 2 | Below average — partially meets requirements |
| 1 | Poor — does not meet requirements |

---

## Custom Criteria Definition

When no standard set applies, define custom criteria:

```yaml
decision_criteria:
  - name: "<criterion name>"
    weight: 0.25           # weights must sum to 1.0
    description: "<what this measures>"
    scoring_guide:
      5: "<what earns a 5>"
      3: "<what earns a 3>"
      1: "<what earns a 1>"
    data_source: "<where to get evidence to score this>"
```

Criteria must:
- Be measurable or assessable from available information
- Be independent of each other (avoid double-counting)
- Weight distribution must sum to 1.0
- Minimum 3 criteria, maximum 8 (beyond 8 becomes cognitively unwieldy)