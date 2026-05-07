# Semantic Chunking Guidelines

Used by `skills/ai-search-optimization/SKILL.md` to guide content authors and auditors
in structuring content for optimal retrieval by AI systems.

---

## Why Chunking Matters

LLMs do not read entire web pages — they retrieve in chunks. When an AI assistant searches
for information, it retrieves the most semantically relevant chunk(s) from a vector index,
not the full page. If your content is not chunked effectively:

- Key information may be split across chunk boundaries and lost
- Context needed to interpret a claim may be in a different chunk
- The AI may cite an incomplete or out-of-context excerpt
- Your content may be outranked by competitors with better structure

---

## Chunking Strategies

| Strategy | Best For | Target Chunk Size | Overlap | Trade-offs |
|---|---|---|---|---|
| Fixed-size | Simple, uniform content | 512 tokens | 50 tokens | Fast but may split mid-sentence |
| Sentence-boundary | Mixed prose content | 200–400 tokens | 1 sentence | Better coherence; may miss structure |
| Semantic | Complex/technical content | 300–600 tokens | Contextual | Best retrieval; requires NLP tooling |
| Hierarchical | Documentation, guides | Variable | Parent-child | Best for navigation; complex to index |
| Paragraph-boundary | Blog posts, articles | 150–300 tokens | 0 | Simple; respects natural breaks |

Recommended default for most sites: **semantic chunking** with H2/H3 boundaries as chunk
delimiters and a 300-token target.

---

## Structural Signals That Define Chunk Boundaries

AI indexers use these HTML/Markdown elements as natural chunk boundaries:

| Element | Boundary Type | Notes |
|---|---|---|
| `<h2>` / `##` | Strong boundary | Start new chunk at every H2 |
| `<h3>` / `###` | Soft boundary | May split or keep with parent H2 |
| `<p>` | Sentence boundary | Two blank lines = stronger break |
| `<ul>` / `<ol>` | Group boundary | Keep list items in same chunk as the list heading |
| `<pre>` / ` ``` ` | Atomic unit | Never split code blocks across chunks |
| `<table>` | Atomic unit | Keep table in one chunk with its caption |
| `<blockquote>` | Inline | Keep with surrounding paragraph |
| `<hr>` / `---` | Strong boundary | Explicit section break |

---

## Content Anti-Patterns

These patterns make content hard to retrieve and cite by AI systems:

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Wall of text (no headers) | No chunk boundaries; whole page = one chunk | Add H2/H3 hierarchy |
| Headers without content | Chunk is empty or uninformative | Ensure each section has ≥2 sentences |
| Key facts buried in long paragraphs | Facts get truncated at chunk boundary | Lead with the key fact, then elaborate |
| JavaScript-rendered content | Not indexed by most AI crawlers | Serve content in SSR or static HTML |
| PDFs without text layer | Not readable | Add OCR layer or provide HTML equivalent |
| Important info in images only | Not retrievable | Add descriptive alt text + caption |
| Duplicate content across pages | Splits retrieval signal | Consolidate or canonicalize |
| Thin pages (<300 words) | Insufficient signal for retrieval | Merge with related content |

---

## Ideal Content Structure for AI Retrieval

```markdown
# Page Title (H1 — one per page)

> One-sentence summary of what this page covers. [Used as chunk intro if separated]

## Section 1: Key Topic (H2)

Lead sentence stating the main point of this section. Supporting detail in 2–4 sentences.
Keep within 300–500 tokens.

### Subsection (H3, optional)

Specific detail. May be kept with parent H2 or chunked separately.

## Section 2: Next Topic (H2)

...
```

---

## Measurement: Evaluating Chunk Quality

| Metric | How to Measure | Target |
|---|---|---|
| Retrieval precision | Ask an AI assistant a question whose answer is on your page; check if it cites your page | >70% of questions answered with correct citation |
| Chunk coherence | Sample 10 chunks; verify each stands alone as a readable unit | >90% coherent without surrounding context |
| Citation accuracy | Verify AI citations point to the correct section, not a vague page reference | >80% section-accurate |
| Coverage | Audit how many distinct concepts on the page appear in at least one chunk | >95% concept coverage |

Use `scripts/ai-discovery/validate_ai_discovery.py` to run an automated structural audit.