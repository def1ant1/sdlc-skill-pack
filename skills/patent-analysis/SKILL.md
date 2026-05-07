---
name: patent-analysis
description: Analyzes patent landscapes to identify freedom-to-operate risks, competitive IP positions, white space opportunities, and prior art relevant to technology decisions.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [research-runtime, legal-ops, knowledge-graph, enterprise-search]
---

## Role

Patent landscape intelligence specialist. Supports technology decisions, product development,
and IP strategy by analyzing patent filings, identifying freedom-to-operate risks, mapping
competitor IP positions, and finding white space opportunities for novel approaches.

## Activation Triggers

- New technology direction requires FTO (freedom-to-operate) assessment
- Competitive patent landscape analysis requested
- Prior art search needed to support IP strategy
- Partnership or acquisition requiring IP due diligence

## Execution Protocol

1. **Define analysis scope**: Clarify technology domain, key claims of interest, relevant
   jurisdictions, and time window for patent search.

2. **Search patent corpus**: Query patent databases for relevant patents by: technology
   keywords, IPC/CPC classification codes, assignee (competitor), inventor, and citation network.

3. **Classify relevance**: Score each patent by relevance to the technology in question;
   retain high-relevance patents for detailed analysis.

4. **Map IP landscape**: Group patents by assignee, technology cluster, and claim scope;
   identify dominant IP holders and white space areas.

5. **Assess FTO risks**: For each high-relevance patent, assess: claim scope vs. planned
   implementation, expiration date, jurisdiction coverage, and likelihood of conflict.

6. **Produce IP analysis report**: Landscape map, FTO risk assessment, white space opportunities,
   recommended design-arounds, and recommended legal review items.

## Output Format

IP analysis report with: patent landscape heatmap by assignee/technology cluster, ranked FTO
risks with claim analysis, white space opportunities, and referrals to legal-ops for counsel review.

## References

- `references/patent-analysis-methodology.md` — search strategy, claim analysis framework, FTO risk scoring, legal referral criteria