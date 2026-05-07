# Editorial Calendar Template

Used by `skills/content-marketing/SKILL.md` to structure the rolling 4–8 week
editorial calendar, define status labels, and apply prioritization rules.

---

## Calendar Structure

| Week | Date | Title / Topic | Channel | Format | Target KW / Audience | Status | Owner | Priority |
|---|---|---|---|---|---|---|---|---|
| W1 | YYYY-MM-DD | [title] | Blog | Long-form | [keyword] | Draft | Content | P0 |
| W1 | YYYY-MM-DD | [title] | Newsletter | Digest | — | Scheduled | Content | P0 |
| W1 | YYYY-MM-DD | [title] | LinkedIn | Carousel | Engineers | Brief | Content | P1 |
| W2 | YYYY-MM-DD | [title] | Blog | Long-form | [keyword] | Ideation | Content | P1 |

---

## Status Labels

| Status | Definition | Next Action |
|---|---|---|
| `Ideation` | Topic identified; no brief yet | Write content brief |
| `Brief` | Content brief complete | Start draft |
| `Draft` | First draft written | Send for review |
| `Review` | Under review | Incorporate feedback |
| `Approved` | Approved by operator | Schedule for publish |
| `Scheduled` | In publishing queue | Monitor publish |
| `Published` | Live | Log publish date; track metrics |
| `Repurpose` | Published; ready to be adapted | Create derivative content |
| `Blocked` | Waiting on dependency | Identify and resolve blocker |
| `Cancelled` | Will not publish | Archive with reason |

---

## Priority Labels

| Priority | Definition | Examples |
|---|---|---|
| P0 | Launch-critical; cannot slip | Launch announcement, Product Hunt copy, launch blog |
| P1 | High-impact; should ship on schedule | Core SEO pillar posts, weekly newsletter |
| P2 | Valuable; can slip one week | Social series, YouTube tutorial |
| P3 | Nice-to-have; ship when capacity allows | Repurposed content, Reddit posts |

---

## Content Mix Guidelines

For a typical 4-week sprint, aim for this mix:

| Content Type | Volume | Rationale |
|---|---|---|
| SEO blog posts (long-form) | 2–4 | Foundation for organic + AI traffic |
| Newsletter issues | 4 | Weekly retention touchpoint |
| LinkedIn posts | 12–20 | Daily B2B awareness |
| X / Twitter posts | 20–28 | Daily developer community |
| Reddit posts | 2–4 | Community credibility |
| Product Hunt / launch | 1 (per launch) | Launch-day spike |
| YouTube videos | 1–2 | Educational depth |

Adjust based on team capacity. Reduce volume before reducing quality.

---

## Pillar + Cluster SEO Model

Organize blog content around topic clusters:

```
Pillar page (2000–4000 words) — targets broad keyword
  ├── Cluster post 1 (1000–1500 words) — targets long-tail variant
  ├── Cluster post 2 (1000–1500 words) — targets long-tail variant
  ├── Cluster post 3 (1000–1500 words) — targets long-tail variant
  └── Cluster post 4 (1000–1500 words) — targets long-tail variant
```

Each cluster post links back to the pillar. The pillar links to all cluster posts.
This structure is also the best pattern for AI retrieval (clear topic hierarchy + internal linking).

---

## Repurposing Workflow

Each long-form blog post can become:

```
Blog post (1500+ words)
  → LinkedIn carousel (10 slides with key insights)
  → Twitter/X thread (10–15 tweets with data points)
  → Newsletter section (300-word summary + link)
  → YouTube video script (tutorial or talking-head commentary)
  → Reddit post ("We learned X after doing Y — full writeup in comments")
```

Plan repurposing when creating the content brief — identify which channels each piece
will feed before writing the first draft.