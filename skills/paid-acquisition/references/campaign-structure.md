# Paid Acquisition — Campaign Structure & UTM Taxonomy

## Campaign Hierarchy

```
ACCOUNT
└── Campaign (budget, bidding, channel, objective)
    └── Ad Group (audience segment, keyword group)
        └── Ad Variants (3–5 per ad group)
            └── Landing Page (1:1 with ad group intent)
```

---

## Naming Convention

### Campaign Name Format

```
{Channel}_{Intent Stage}_{Target ICP}_{Offer}_{YYYY-MM}

Examples:
  Google_Search_BoFu_Enterprise_FreeTrial_2026-05
  LinkedIn_ToFu_DevTools_Awareness_2026-05
  Meta_Retargeting_AllVisitors_TrialOffer_2026-05
```

### Ad Group Name Format

```
{Keyword Theme or Audience Segment}_{Match Type}

Examples:
  AICodeReview_Exact
  SoftwareDevManagers_Broad
  SiteVisitors_30d_Retargeting
```

---

## UTM Parameter Schema

| Parameter | Values | Required | Example |
|-----------|--------|---------|---------|
| `utm_source` | google, linkedin, meta, reddit, email | Yes | `google` |
| `utm_medium` | cpc, cpm, email, organic, referral | Yes | `cpc` |
| `utm_campaign` | Matches campaign name (kebab-case) | Yes | `google-search-bofu-enterprise-2026-05` |
| `utm_content` | Creative ID or variant descriptor | Recommended | `headline-v2` |
| `utm_term` | Keyword (Search) or audience (Social) | Recommended | `ai-code-review` |

**UTM Builder formula:**
```
{landing_page_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={creative_id}&utm_term={keyword}
```

---

## Intent Stage Definitions

| Stage | Name | Goal | Budget % |
|-------|------|------|---------|
| ToFu | Top of Funnel | Brand awareness, problem education | 15% |
| MoFu | Middle of Funnel | Solution evaluation, feature education | 25% |
| BoFu | Bottom of Funnel | Conversion (trial, demo, purchase) | 45% |
| Retargeting | Site Visitor Retargeting | Re-engage non-converts | 15% |

---

## Bid Strategy Rules

| Condition | Recommended Strategy | Notes |
|-----------|---------------------|-------|
| ≥ 30 conversions/month in campaign | Target CPA | Sufficient data for smart bidding |
| < 30 conversions/month | Manual CPC with bid adjustments | Maximize control |
| Brand search campaigns | Target impression share (≥ 90%) | Protect brand |
| Display / awareness | Target CPM with frequency cap | Cap at 7 impressions/user/week |
| Retargeting | Target CPA (lower than prospecting) | Warmer audience, higher CVR expected |

---

## Negative Keyword Lists

See `references/negative-keyword-lists.md` for full lists. Standard negatives to apply to all Search campaigns:

```
free, open source, tutorial, course, certification, job, jobs, career, salary,
wikipedia, reddit, github, youtube, crack, pirate, torrent, download free,
interview questions, how to learn, bootcamp
```

---

## A/B Testing Framework for Ads

| Element | Test Method | Minimum Volume | Winner Criterion |
|---------|------------|----------------|-----------------|
| Headline | Rotate evenly; Google Experiments | 1,000 impressions per variant | CTR ≥ 20% lift, p < 0.05 |
| CTA text | Single variable test | 500 conversions per variant | CVR ≥ 10% lift |
| Landing page | Google Experiments (50/50 split) | 200 conversions per variant | CVR ≥ 10% lift, p < 0.05 |
| Audience segment | Separate ad groups | 500 impressions each | CPA ≤ target |

---

## Campaign Health Dashboard

| Metric | Check Frequency | Alert If |
|--------|----------------|---------|
| Daily spend vs. budget | Daily | > 110% or < 80% of daily budget |
| CPA trend (7-day rolling) | Weekly | > 150% of target CPA |
| CTR | Weekly | < 1% (Search), < 0.5% (Display/Social) |
| Quality Score (Google) | Weekly | < 6 on any active keyword |
| Impression share | Weekly | < 70% on branded keywords |
| Conversion rate | Weekly | < 50% of landing page CVR target |