# GTM Router

Used by `core/gtm-orchestration/SKILL.md` to map natural-language GTM intents to skill
routes and gate sequences.

---

## Intent-to-Skill Routing Table

| Intent Signal | Primary Skill | Supporting Skills | Gate Before Next |
|---|---|---|---|
| "launch", "go live", "ship", "release to market" | launch-planning | seo-engineering, content-marketing | launch-plan-approved |
| "SEO", "search ranking", "organic traffic", "backlinks", "technical SEO" | seo-engineering | ai-search-optimization | seo-baseline-complete |
| "AI search", "LLM discovery", "llms.txt", "answer engine", "ChatGPT visibility" | ai-search-optimization | seo-engineering | ai-discovery-validated |
| "content", "blog", "article", "newsletter", "editorial calendar" | content-marketing | seo-engineering | content-strategy-approved |
| "paid ads", "Google Ads", "Meta Ads", "PPC", "acquisition", "CAC" | paid-acquisition | analytics-intelligence | campaign-brief-approved |
| "analytics", "dashboard", "metrics", "funnel", "attribution", "conversion" | analytics-intelligence | — | analytics-baseline-set |
| "customer success", "onboarding", "churn", "NPS", "retention", "CSAT" | customer-success | analytics-intelligence | onboarding-flow-live |
| "revenue", "pricing", "upsell", "expansion", "ARR", "MRR", "LTV" | revenue-optimization | analytics-intelligence, customer-success | revenue-model-approved |
| "positioning", "ICP", "messaging", "value proposition", "competitive" | launch-planning | content-marketing | positioning-approved |
| "influencer", "partnership", "co-marketing", "affiliate" | content-marketing | paid-acquisition | partnership-brief-approved |

---

## Confidence Mapping

| Confidence | Condition | Action |
|---|---|---|
| `high` | 2+ primary signals match | Route directly |
| `medium` | 1 primary + 1 supporting signal | Route, note uncertainty |
| `low` | Supporting signals only | Ask one clarifying question |
| `unknown` | No signals match | Ask one clarifying question, offer 3 options |

---

## Multi-Phase Detection

When two or more intents match with `medium` or higher confidence, classify as `multi-phase`
and resolve the full dependency chain using `launch-workflow-map.md`.

| Pattern | Phases | Complexity |
|---|---|---|
| Launch + SEO + Content | launch-planning → seo-engineering → content-marketing | multi-phase |
| Full GTM | All 8 phases | full-gtm |
| SEO + AI Discovery | seo-engineering → ai-search-optimization | multi-phase |
| Paid + Analytics | paid-acquisition + analytics-intelligence (parallel) | multi-phase |
| Retention + Revenue | customer-success → revenue-optimization | multi-phase |