# SEO Engineering — Keyword Map Schema

## Keyword Map Schema

```yaml
keyword_map_entry:
  url: "https://example.com/features/ai-code-review"
  page_type: feature | blog | landing | docs | home | pricing
  primary_keyword:
    keyword: "AI code review"
    monthly_search_volume: 2400
    keyword_difficulty: 52    # [0, 100]; higher = harder
    intent: informational | navigational | commercial | transactional
    current_position: 18      # null if not ranking
    target_position: 5
  secondary_keywords:
    - keyword: "automated code review tool"
      volume: 880
      intent: commercial
    - keyword: "code review AI assistant"
      volume: 590
      intent: commercial
    - keyword: "AI pull request review"
      volume: 320
      intent: transactional
  title_tag: "AI Code Review Tool — Automated PR Reviews | Apotheon"
  meta_description: "Apotheon's AI code review catches bugs, security issues, and style violations automatically. Cut review time by 60%. Try free."
  h1: "AI-Powered Code Review"
  internal_links_from:
    - "https://example.com/features"
    - "https://example.com/blog/ai-code-quality"
  status: live | draft | planned
  last_optimized: "2026-05-07"
```

---

## Keyword Intent Classification

| Intent | Search Pattern | Landing Page Type | CTA |
|--------|---------------|------------------|-----|
| Informational | "what is...", "how to...", "guide to..." | Blog, docs | Subscribe, learn more |
| Navigational | Brand name, product name | Homepage, feature pages | Get started |
| Commercial | "best...", "top...", "alternatives to...", "reviews" | Feature, comparison | Free trial, demo |
| Transactional | "buy...", "pricing", "sign up for..." | Pricing, signup | Buy now, start free |

---

## Keyword Priority Matrix

```
High Volume + Low Difficulty → WIN NOW (top priority)
High Volume + High Difficulty → LONG-TERM INVEST (quality content + links needed)
Low Volume + Low Difficulty → QUICK WIN (implement fast, low effort)
Low Volume + High Difficulty → DEPRIORITIZE (poor ROI)
```

| Volume | Difficulty | Priority | Action |
|--------|-----------|---------|--------|
| > 1,000/mo | < 40 | P0 | Optimize immediately |
| > 1,000/mo | 40–70 | P1 | Build content + backlinks |
| 200–999/mo | < 40 | P1 | Optimize within quarter |
| < 200/mo | < 30 | P2 | Include in existing content |
| Any | > 70 | P3 | Monitor; enter only with authority |

---

## Content Gap Tracking

```yaml
content_gap:
  keyword: "Temporal workflow orchestration Python"
  volume: 1600
  difficulty: 38
  intent: informational
  competitor_ranking_url: "https://temporal.io/blog/..."
  competitor_position: 3
  our_current_position: null
  gap_type: missing_content | underoptimized_page | link_deficit
  recommended_action: "Create new blog post: 'Getting Started with Temporal Workflow Orchestration in Python'"
  estimated_time_to_rank_months: 3
  priority: P0
```

---

## Cannibalization Register

If two pages target the same primary keyword, one must be consolidated or redirected.

```yaml
cannibalization_issue:
  keyword: "AI code review"
  competing_urls:
    - url: "https://example.com/features/ai-code-review"
      ranking_position: 18
    - url: "https://example.com/blog/ai-code-review-guide"
      ranking_position: 24
  resolution: consolidate_into_feature | redirect_blog_to_feature | differentiate_intent
  action_taken: null
  resolved_at: null
```