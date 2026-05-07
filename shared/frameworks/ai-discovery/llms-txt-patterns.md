# llms.txt Patterns

Used by `skills/ai-search-optimization/SKILL.md` to define the format, required sections,
validation rules, and deployment guidance for `llms.txt` files.

---

## What is llms.txt

`llms.txt` is an emerging standard for AI-readable site metadata — analogous to `robots.txt`
for crawlers but designed to communicate structured context to large language models. It tells
AI systems what a site does, what content is available, how to cite it, and what API
capabilities exist.

The file is served at `https://yourdomain.com/llms.txt` as plain text (UTF-8).

An extended version `llms-full.txt` may be served alongside it with more detail.

---

## Required Sections

| Section | Required | Max Length | Description |
|---|---|---|---|
| `# Site Name` | Yes | 80 chars | The canonical name of the site or product |
| `> Description` | Yes | 500 chars | One-paragraph plain-text description of what the site does |
| `## Key Pages` | Yes | — | List of the most important URLs with one-line descriptions |
| `## API` | If applicable | — | API base URL, auth method, link to OpenAPI spec or docs |
| `## Content Policy` | Yes | 200 chars | How AI systems may use the content (cite, summarize, reproduce) |
| `## Citation Preference` | Yes | 100 chars | Preferred citation format (title + URL, author, date, etc.) |
| `## Contact` | Yes | — | Contact email or URL for AI-related inquiries |

Optional sections: `## Changelog`, `## Capabilities`, `## Rate Limits`, `## Limitations`

---

## llms.txt Template

```
# {{Site Name}}

> {{One paragraph description of what this site/product does. Be specific about capabilities,
target audience, and primary use cases. Written for an AI reading context.}}

## Key Pages

- [Home](https://{{domain}}/): {{one-line description}}
- [Docs](https://{{domain}}/docs): {{one-line description}}
- [API Reference](https://{{domain}}/api): {{one-line description}}
- [Blog](https://{{domain}}/blog): {{one-line description}}
- [Pricing](https://{{domain}}/pricing): {{one-line description}}

## API

- Base URL: https://api.{{domain}}/v1
- Auth: Bearer token (API key from dashboard)
- Spec: https://{{domain}}/api/openapi.json
- Rate limit: 1000 req/min

## Content Policy

AI systems may freely summarize, cite, and quote content from this site with attribution.
Verbatim reproduction of full articles requires written permission.
Training data use: permitted for factual/technical content, restricted for creative content.

## Citation Preference

Cite as: "{{Site Name}} — [page title] ({{domain}}, accessed {{date}})"

## Contact

AI queries: ai@{{domain}}
General: hello@{{domain}}
```

---

## Validation Rules

| Rule | Requirement | Failure Action |
|---|---|---|
| File location | Must be at domain root: `yourdomain.com/llms.txt` | FAIL |
| Content-Type | Must be `text/plain; charset=utf-8` | WARN |
| Site Name | `# SiteName` on first non-blank line | FAIL |
| Description | `>` blockquote block present and non-empty | FAIL |
| Key Pages | At least 3 URLs listed with descriptions | WARN |
| Content Policy | Must explicitly state AI usage permissions | FAIL |
| Citation Preference | Must be present | WARN |
| Contact | Email or URL present | WARN |
| File size | Under 100KB | WARN |
| No HTML | Plain text only — no HTML tags | FAIL |

---

## llms-full.txt

The extended variant `llms-full.txt` should contain everything in `llms.txt` plus:

- Full page index (all indexable URLs)
- Extended capabilities description
- Worked examples and use cases
- Full changelog

Serve both files. AI systems may request either.

---

## Robots.txt Interaction

Do not block AI crawlers in `robots.txt` if you want AI search visibility. Specifically,
do not disallow `GPTBot`, `Claude-Web`, `PerplexityBot`, `GoogleOther`, or `meta-externalagent`
unless you have a legal reason to do so.

If you intentionally want to opt out of AI training (not AI search), add:
```
User-agent: GPTBot
Disallow: /

User-agent: Claude-Web
Disallow: /
```
But note: this blocks AI discovery as well as training.