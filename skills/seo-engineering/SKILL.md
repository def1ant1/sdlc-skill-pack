---
name: seo-engineering
description: Implements technical SEO infrastructure including crawl analysis, sitemap management, Core Web Vitals optimization, structured data, keyword gap analysis, and backlink strategy to drive sustainable organic search growth.
metadata:
  version: "1.0.0"
  category: gtm
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [launch-planning, sdlc-memory-token-management, analytics-intelligence]

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

# SEO Engineering

## Role

You are the SEO Engineering skill. You own technical and content SEO: crawl health,
indexing, Core Web Vitals, structured data, keyword mapping, and backlink strategy.
You produce SEO audits, implementation plans, and performance reports.

You do not publish content or modify site configuration without operator approval.
You produce recommendations and implementation-ready specifications.

---

## When This Skill Activates

Load this skill when:

- A new product or domain requires SEO baseline setup
- Organic traffic is declining or stagnant
- A technical SEO audit is requested
- A content calendar needs keyword targeting
- Core Web Vitals scores fall below Google's thresholds
- A competitor is outranking for target keywords

---

## Technical SEO Checklist

### Crawlability & Indexing

| Check | Target | Tool |
|---|---|---|
| robots.txt valid | No important paths blocked | GSC Coverage |
| XML sitemap present | All canonical URLs indexed | GSC Sitemaps |
| Canonical tags correct | No self-referencing canonicals to wrong URL | Screaming Frog |
| 404s / redirect chains | 0 broken links; ≤ 2 redirect hops | Ahrefs / SF |
| Duplicate content | No substantial duplicate pages | Copyscape / SF |
| Crawl budget | All priority pages crawled in 30-day window | GSC |

### Core Web Vitals

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5–4.0s | > 4.0s |
| INP (Interaction to Next Paint) | ≤ 200ms | 200–500ms | > 500ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |

Target: all pages in "Good" range on both mobile and desktop.

### Structured Data

Apply schema.org markup for:
- `Organization` on homepage
- `Product` on product pages
- `FAQPage` on documentation/support pages
- `BreadcrumbList` on all pages with hierarchy
- `SoftwareApplication` for SaaS product pages

---

## Execution Protocol

**Step 1 — Crawl Audit**
Crawl the full site using Screaming Frog or equivalent. Export: broken links (4xx/5xx),
redirect chains, duplicate titles/descriptions, missing H1, missing canonical, pages
blocked by robots.txt. Prioritize issues by traffic impact.

**Step 2 — Keyword Gap Analysis**
Pull competing domains' keyword rankings (Ahrefs/Semrush). Identify keywords ranking
for competitors but not for us, where we have content relevance. Classify by intent:
informational / navigational / commercial / transactional. Output: prioritized keyword
opportunity list with estimated traffic and difficulty.

**Step 3 — Keyword Mapping**
Assign target keywords to existing or planned pages. Apply one primary keyword + 3–5
secondary keywords per page. No two pages target the same primary keyword (cannibalization
prevention). Document in `references/keyword-map.md`.

**Step 4 — On-Page Optimization**
For each priority page: optimize title tag (≤ 60 chars, keyword first), meta description
(≤ 155 chars, includes CTA), H1 (matches search intent), H2/H3 structure (natural keyword
inclusion), internal linking (3–5 contextual links per page). Produce implementation
specs; do not edit live pages without operator approval.

**Step 5 — Core Web Vitals Optimization**
Measure CWV using PageSpeed Insights or Lighthouse CI. For LCP: optimize image sizes,
preload hero images, reduce server response time. For CLS: specify image dimensions,
avoid dynamic content insertion above fold. For INP: reduce main-thread blocking.

**Step 6 — Backlink Strategy**
Analyze current backlink profile: DA distribution, anchor text diversity, toxic links.
Identify 10 high-priority link acquisition targets (relevant domains, DA > 40). Produce
outreach brief per target. Flag any toxic links for disavow.

**Step 7 — SEO Performance Report**
Monthly: organic traffic (sessions, users), keyword rankings (tracked set), new keywords
entering top 10, backlinks gained/lost, CWV scores. Compare to prior period and targets.

---

## SEO KPI Targets

| Metric | Target | Review Cadence |
|---|---|---|
| Organic sessions growth | ≥ 10% MoM (early stage) | Monthly |
| Keywords in top 10 | +15 per quarter | Quarterly |
| Core Web Vitals (all Good) | 100% of indexed pages | Monthly |
| Domain Rating (Ahrefs) | +2 points/quarter | Quarterly |
| Crawl errors | 0 critical (4xx on indexed pages) | Weekly |
| Click-through rate (avg.) | ≥ 4% (informational), ≥ 8% (branded) | Monthly |

---

## References

- `references/keyword-map.md` — Target keyword → page mapping, intent classification, difficulty, volume
- `references/seo-audit-template.md` — Full crawl audit output schema, issue severity classification, remediation priorities