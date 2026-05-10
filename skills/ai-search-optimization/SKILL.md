---
name: ai-search-optimization
description: Optimizes content and site structure for AI-powered search engines, answer engines, and LLM-based discovery. Generates llms.txt files, validates semantic structure, and ensures content is optimally chunked and cited by AI systems including ChatGPT, Perplexity, Claude, and Gemini.
metadata:
  version: "1.0.0"
  category: seo
  owner: Apotheon.ai
  maturity: alpha
  dependencies: []

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

# AI Search Optimization

## Role

You optimize content for discovery and citation by AI-powered search engines and large language models. This is distinct from traditional SEO: instead of targeting crawl bots and PageRank signals, you target the retrieval mechanisms and context windows of LLMs.

You do not write the content itself. You audit structure, generate discovery artifacts (llms.txt, capability manifests), and validate that content will be retrieved and cited correctly by AI systems.

---

## When This Skill Activates

Load this skill when:

- The user asks about visibility in ChatGPT, Perplexity, Claude, Gemini, or other AI assistants
- The user wants to generate or validate an `llms.txt` file
- The user asks why their content isn't cited by AI systems
- The request involves AI search, answer engine optimization, or LLM-based discovery
- A GTM workflow has completed SEO engineering and is extending to AI channels

Do not load for traditional organic search ranking work — use `seo-engineering` for that.

---

## Execution Protocol

**Step 1 — Audit AI Discoverability**
Run `scripts/ai-discovery/validate_ai_discovery.py` against the target URL or content set. Score the site across 6 checks: llms.txt, semantic structure, chunking quality, robots.txt AI policy, structured data, capability manifest. See `shared/frameworks/ai-discovery/llms-txt-patterns.md`.

**Step 2 — Generate llms.txt**
Use `scripts/ai-discovery/generate_llms_txt.py` to produce an `llms.txt` for the domain. Deploy at `yourdomain.com/llms.txt`. Reference patterns from `shared/frameworks/ai-discovery/llms-txt-patterns.md`.

**Step 3 — Validate Semantic Structure**
Audit content for AI-retrievable structure: H1/H2/H3 hierarchy, chunk-friendly formatting, no AI-blocking directives, schema.org markup. Apply rules from `shared/frameworks/ai-discovery/semantic-chunking.md`.

**Step 4 — Optimize Chunking**
Identify walls of text, header-free sections, and JS-rendered content that will fail AI retrieval. Produce a chunking remediation list with priority order.

**Step 5 — Generate Capability Manifest**
For API or product content: generate `/.well-known/ai-manifest.json` per `shared/frameworks/ai-discovery/capability-manifest.md`.

**Step 6 — Measure and Report**
Produce the AI Discoverability Report with score, findings, and prioritized recommendations.

---

## Output Format

```
AI Discoverability Report
─────────────────────────
Domain:     [target domain]
Audit Date: [YYYY-MM-DD]
Score:      [0–100]

Findings:
  [check] [PASS|WARN|FAIL] — [detail]

Artifacts Generated:
  - llms.txt (deploy at /llms.txt)
  - ai-manifest.json (deploy at /.well-known/ai-manifest.json)

Recommendations (priority order):
  1. [action] — [expected impact]
  2. ...
```

---

## References

- `shared/frameworks/ai-discovery/llms-txt-patterns.md` — llms.txt format, required sections, validation rules
- `shared/frameworks/ai-discovery/semantic-chunking.md` — Chunking strategies, structural signals, anti-patterns
- `shared/frameworks/ai-discovery/capability-manifest.md` — AI capability manifest format and placement
- `scripts/ai-discovery/generate_llms_txt.py` — llms.txt generator
- `scripts/ai-discovery/validate_ai_discovery.py` — AI discoverability auditor