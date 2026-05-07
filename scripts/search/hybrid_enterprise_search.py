#!/usr/bin/env python3
"""
hybrid_enterprise_search.py — Hybrid BM25 + semantic enterprise search (local implementation).

Provides keyword search over the indexed content manifest from index_domain_content.py.
In production, this connects to Qdrant (vector) + BM25 index. This script implements
the BM25/keyword layer as a local fallback that works without external dependencies.

Usage:
    python scripts/search/hybrid_enterprise_search.py --query "SLO definition" --index index.json
    python scripts/search/hybrid_enterprise_search.py --query "governance invariants" --top 5

The index.json is produced by index_domain_content.py.
"""

import json
import math
import re
import sys
from pathlib import Path


def tokenize(text: str) -> list[str]:
    """Simple word tokenizer with lowercasing."""
    return re.findall(r"[a-z0-9]+", text.lower())


def build_bm25_index(documents: list[dict]) -> dict:
    """Build an in-memory BM25 index from document list."""
    k1 = 1.5
    b = 0.75

    # Compute document frequencies
    doc_count = len(documents)
    df: dict[str, int] = {}
    doc_lengths = []

    for doc in documents:
        tokens = tokenize(doc.get("content", "") + " " + doc.get("title", ""))
        doc_lengths.append(len(tokens))
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1

    avg_dl = sum(doc_lengths) / max(doc_count, 1)

    return {
        "documents": documents,
        "df": df,
        "doc_count": doc_count,
        "doc_lengths": doc_lengths,
        "avg_dl": avg_dl,
        "k1": k1,
        "b": b,
    }


def bm25_score(index: dict, query_tokens: list[str], doc_index: int) -> float:
    """Compute BM25 score for a document given query tokens."""
    k1 = index["k1"]
    b = index["b"]
    dl = index["doc_lengths"][doc_index]
    avg_dl = index["avg_dl"]
    doc_count = index["doc_count"]
    df = index["df"]

    doc = index["documents"][doc_index]
    doc_tokens = tokenize(doc.get("content", "") + " " + doc.get("title", ""))
    tf: dict[str, int] = {}
    for t in doc_tokens:
        tf[t] = tf.get(t, 0) + 1

    score = 0.0
    for token in query_tokens:
        if token not in df:
            continue
        idf = math.log((doc_count - df[token] + 0.5) / (df[token] + 0.5) + 1)
        term_freq = tf.get(token, 0)
        numerator = term_freq * (k1 + 1)
        denominator = term_freq + k1 * (1 - b + b * dl / avg_dl)
        score += idf * numerator / denominator

    return score


def search(index: dict, query: str, top_k: int = 5, category_filter: str = "") -> list[dict]:
    """Run BM25 search and return ranked results."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scored = []
    for i, doc in enumerate(index["documents"]):
        if category_filter and doc.get("category") != category_filter:
            continue
        score = bm25_score(index, query_tokens, i)
        if score > 0:
            scored.append((score, i, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    seen_sources: set[str] = set()

    for score, i, doc in scored[:top_k * 3]:  # over-fetch to deduplicate by source
        source = doc["source"]
        # Prefer first chunk of each source in results
        if source in seen_sources:
            continue
        seen_sources.add(source)

        # Extract a relevant snippet
        content = doc.get("content", "")
        snippet = extract_snippet(content, query_tokens)

        results.append({
            "rank": len(results) + 1,
            "score": round(score, 4),
            "source": source,
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "snippet": snippet,
        })

        if len(results) >= top_k:
            break

    return results


def extract_snippet(content: str, query_tokens: list[str], context_chars: int = 200) -> str:
    """Extract a relevant snippet from content around the first query term match."""
    content_lower = content.lower()
    best_pos = -1

    for token in query_tokens:
        pos = content_lower.find(token)
        if pos != -1:
            best_pos = pos
            break

    if best_pos == -1:
        return content[:context_chars].strip() + "..."

    start = max(0, best_pos - 50)
    end = min(len(content), best_pos + context_chars)
    snippet = content[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    return snippet


def print_results(results: list[dict], query: str) -> None:
    """Print search results in human-readable format."""
    print(f"\nSearch: \"{query}\"")
    print(f"Results: {len(results)}")
    print("=" * 60)

    if not results:
        print("No results found.")
        return

    for r in results:
        print(f"\n[{r['rank']}] {r['title']}")
        print(f"    Source:   {r['source']}")
        print(f"    Category: {r['category']} | Score: {r['score']}")
        print(f"    Snippet:  {r['snippet'][:200]}")


def main() -> int:
    args = sys.argv[1:]
    query = ""
    index_file = Path("index.json")
    top_k = 5
    output_json = False
    category_filter = ""

    i = 0
    while i < len(args):
        if args[i] == "--query" and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif args[i] == "--index" and i + 1 < len(args):
            index_file = Path(args[i + 1])
            i += 2
        elif args[i] == "--top" and i + 1 < len(args):
            top_k = int(args[i + 1])
            i += 2
        elif args[i] == "--json":
            output_json = True
            i += 1
        elif args[i] == "--category" and i + 1 < len(args):
            category_filter = args[i + 1]
            i += 2
        else:
            i += 1

    if not query:
        print("ERROR: --query is required", file=sys.stderr)
        return 1

    if not index_file.exists():
        print(f"ERROR: Index file not found: {index_file}", file=sys.stderr)
        print("Run: python scripts/search/index_domain_content.py --output index.json", file=sys.stderr)
        return 1

    documents = json.loads(index_file.read_text(encoding="utf-8"))
    index = build_bm25_index(documents)
    results = search(index, query, top_k, category_filter)

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results, query)

    return 0


if __name__ == "__main__":
    sys.exit(main())