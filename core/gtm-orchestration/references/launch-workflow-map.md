# Launch Workflow Map

Used by `core/gtm-orchestration/SKILL.md` to sequence GTM phases, define SDLC-to-GTM
handoff artifacts, and identify parallel execution opportunities.

---

## SDLC-to-GTM Handoff

GTM execution begins once the following SDLC artifacts are available:

| SDLC Artifact | Source Phase | GTM Consumer | Required For |
|---|---|---|---|
| Product requirements doc | requirements-engineering | launch-planning | ICP, messaging |
| Architecture decision record | system-architecture | seo-engineering | Technical SEO, sitemap |
| API documentation | backend-engineering | ai-search-optimization | Capability manifest, llms.txt |
| Security review report | devsecops | paid-acquisition | Ad compliance, trust signals |
| Release notes | release-management | content-marketing | Launch blog, changelog |
| Observability runbook | observability | customer-success | Support escalation paths |

GTM may start `launch-planning` in parallel with the final SDLC phases when the
product is feature-complete and in QA.

---

## GTM Phase Sequence

| # | GTM Phase | Inputs From | Outputs To | Gate | Parallel With |
|---|---|---|---|---|---|
| 1 | launch-planning | SDLC handoff artifacts | All GTM phases | launch-plan-approved | — |
| 2 | seo-engineering | launch-planning | ai-search-optimization, content-marketing | seo-baseline-complete | content-marketing |
| 3 | content-marketing | launch-planning, seo-engineering | paid-acquisition | content-strategy-approved | seo-engineering |
| 4 | ai-search-optimization | seo-engineering, API docs | — | ai-discovery-validated | paid-acquisition |
| 5 | paid-acquisition | launch-planning, content-marketing | analytics-intelligence | campaign-brief-approved | analytics-intelligence, ai-search-optimization |
| 6 | analytics-intelligence | All active phases | revenue-optimization | analytics-baseline-set | paid-acquisition |
| 7 | customer-success | launch-planning, release notes | revenue-optimization | onboarding-flow-live | — |
| 8 | revenue-optimization | analytics-intelligence, customer-success | — | revenue-model-approved | — |

---

## Dependency Graph

```
launch-planning
├── seo-engineering ─────────────────────┐
│   └── ai-search-optimization           │
│                                        ▼
└── content-marketing                paid-acquisition ─┐
    └── paid-acquisition (feeds)          │             │
                                          ▼             ▼
                                   analytics-intelligence
                                          │
customer-success ─────────────────────────┤
                                          ▼
                                  revenue-optimization
```

---

## Launch Timeline Template

| Week | Activities | Gate |
|---|---|---|
| -4 | ICP finalization, messaging framework, SEO audit | positioning-approved |
| -3 | Content production, keyword mapping, AI discovery setup | content-strategy-approved |
| -2 | Paid campaign setup, landing page QA, analytics instrumentation | campaign-brief-approved |
| -1 | Soft launch, PR embargo lift, influencer outreach | launch-plan-approved |
| 0 | Public launch, paid go-live, press release, social push | — |
| +1 | Analytics review, CAC/conversion baseline, onboarding metrics | analytics-baseline-set |
| +4 | Retention review, churn analysis, upsell identification | onboarding-flow-live |
| +8 | Revenue model review, pricing optimization, expansion planning | revenue-model-approved |

---

## Pre-Launch Checklist

```
[ ] ICP and positioning documented
[ ] SEO technical audit passed
[ ] llms.txt deployed at domain root
[ ] Analytics tracking verified (GA4, Mixpanel, or equivalent)
[ ] Paid campaigns reviewed and approved
[ ] Landing page conversion tested
[ ] Customer onboarding flow tested end-to-end
[ ] Support runbook distributed to CS team
[ ] Launch communications scheduled (blog, email, social)
[ ] Revenue reporting dashboard live
```