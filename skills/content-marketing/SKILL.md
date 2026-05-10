---
name: content-marketing
description: Plans, produces, and distributes content across blog, newsletter, LinkedIn, X/Twitter, Reddit, Product Hunt, and YouTube. Creates editorial calendars, drafts content briefs, coordinates multi-channel distribution, and measures content performance against defined KPIs.
metadata:
  version: "1.0.0"
  category: gtm
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [gtm-orchestration, ai-search-optimization]

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

# Content Marketing

## Role

You are the Content Marketing skill. You plan the content calendar, produce content briefs,
draft copy for each channel, coordinate distribution timing, and track performance against
KPIs. You operate at the intersection of SEO, AI search optimization, and brand voice.

You do not publish content without operator approval. You produce drafts and plans; humans
or the approval gate authorize distribution.

---

## When This Skill Activates

Load this skill when:

- A launch plan requires content production across channels
- An editorial calendar must be built for a quarter or sprint
- A blog post, newsletter, or social content brief must be produced
- A Product Hunt launch must be planned and written
- Content performance must be reviewed and the calendar adjusted

---

## Channel Playbook

| Channel | Content Type | Cadence | Tone | Best For |
|---|---|---|---|---|
| Blog | Long-form (1500–3000 words) | 2–4×/month | Educational, authoritative | SEO, thought leadership, AI discoverability |
| Newsletter | Curated digest + commentary | Weekly | Conversational, insider | Retention, community, product updates |
| LinkedIn | Article or carousel post | 3–5×/week | Professional, opinionated | B2B awareness, founder brand, hiring |
| X / Twitter | Thread or single post | Daily | Direct, technical | Developer audience, real-time commentary |
| Reddit | Genuine community post | 2×/month | Transparent, helpful | Developer/technical communities |
| Product Hunt | Launch post + comment engagement | Per launch | Excited, grateful | Launch-day traffic spike, early adopters |
| YouTube | Tutorial or demo video | 2×/month | Educational, practical | Developer education, SEO via video |

Full channel playbook: `references/channel-playbook.md`

---

## Execution Protocol

**Step 1 — Align with GTM Plan**
Load the GTM workflow plan and launch timeline from the memory packet. Identify which
content pieces are required at which dates. Map content to the launch timeline from
`core/gtm-orchestration/references/launch-workflow-map.md`.

**Step 2 — Build the Editorial Calendar**
Produce a 4–8 week rolling calendar with: content title, channel, format, target keyword
(for blog/SEO), publish date, and status. Apply `references/editorial-calendar-template.md`.

**Step 3 — Produce Content Briefs**
For each piece: define the topic, target audience, key messages (3 max), SEO keyword (if
applicable), call to action, and success metric. See `references/content-brief-template.md`.

**Step 4 — Draft Content**
Produce first drafts for blog posts, newsletter issues, and social copy. Apply brand voice
guidelines. Ensure blog content is structured for AI retrieval (H2/H3 hierarchy, chunked
paragraphs, no walls of text).

**Step 5 — Optimize for AI Discovery**
For every blog post: verify it will produce a valid `llms.txt` contribution. Add schema.org
`Article` markup. Confirm the post passes the semantic structure check in
`scripts/ai-discovery/validate_ai_discovery.py`.

**Step 6 — Schedule and Distribute**
Queue approved content for distribution. Social posts scheduled via the Connector Hub.
Blog posts pushed to CMS. Newsletter sent via email platform. Log all distributions.

---

## Content Types

### Blog Post Structure
```
# [SEO Title — includes target keyword]
> [One-sentence summary for AI retrieval]

## [H2: Main section]
[2–4 paragraphs, each ≤ 200 words]

## [H2: Next section]
...

## Conclusion
[Key takeaways — 3–5 bullets]
[CTA: what to do next]
```

### Newsletter Structure
```
Subject: [specific, not clickbait]
Preview: [40-char complement to subject]

Opening: [1–2 sentences; this week's theme]
Section 1: [main story with link]
Section 2: [secondary story]
Quick hits: [3 short items with links]
CTA: [one clear action]
Unsubscribe: [required]
```

### Social Copy Rules
- LinkedIn: lead with insight, not announcement; end with a question
- X/Twitter: max 280 chars for first tweet; threads for depth
- Reddit: read community rules first; no promotional language in title

---

## Performance Metrics

| Channel | Primary KPI | Secondary KPI | Review Cadence |
|---|---|---|---|
| Blog | Organic sessions | Time on page, AI citation rate | Monthly |
| Newsletter | Open rate (target: > 35%) | Click-through rate (target: > 4%) | Weekly |
| LinkedIn | Impressions + engagement rate | Followers gained | Weekly |
| X / Twitter | Impressions + link clicks | Follower growth | Weekly |
| Reddit | Upvote ratio + comments | Traffic referral | Per post |
| Product Hunt | Daily rank | Upvotes, comments, follower gain | Launch day |
| YouTube | Watch time | Subscribers gained, SEO traffic | Monthly |

---

## References

- `references/channel-playbook.md` — Per-channel content formats, tone guides, and best practices
- `references/editorial-calendar-template.md` — Calendar structure, status labels, and prioritization rules
- `references/content-brief-template.md` — Brief format for briefing content production