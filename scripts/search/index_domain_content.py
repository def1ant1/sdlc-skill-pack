#!/usr/bin/env python3
"""
index_domain_content.py — Index platform content for enterprise search.

Scans all SKILL.md files, reference documents, and shared resources, then
produces a search index manifest (JSON) suitable for ingestion into the
vector store (Qdrant) or BM25 index.

Usage:
    python scripts/search/index_domain_content.py [--root .] [--output index.json]

Output: JSON array of indexable documents with metadata.
"""

import hashlib
import json
import re
import sys
from pathlib import Path


INDEXABLE_EXTENSIONS = {".md", ".yaml", ".yml"}
SKIP_DIRECTORIES = {"node_modules", ".git", "__pycache__", ".pytest_cache", "venv"}
MAX_CHUNK_CHARS = 2000
CHUNK_OVERLAP_CHARS = 200


def file_category(path: Path) -> str:
    """Determine content category from file path."""
    parts = path.parts
    if "core" in parts:
        return "skills"
    if "skills" in parts:
        return "skills"
    if "agents" in parts:
        return "agents"
    if "shared/standards" in str(path) or "shared\\standards" in str(path):
        return "standards"
    if "shared/policies" in str(path) or "shared\\policies" in str(path):
        return "policies"
    if "references" in parts:
        return "references"
    if "docs" in parts:
        return "documents"
    if "scripts" in parts:
        return "scripts"
    return "other"


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end < len(text):
            # Try to break at a paragraph boundary
            break_at = text.rfind("\n\n", start, end)
            if break_at == -1:
                break_at = text.rfind("\n", start, end)
            if break_at > start:
                end = break_at
        chunks.append(text[start:end].strip())
        start = end - overlap
        if start <= 0:
            start = end

    return [c for c in chunks if c]


def content_hash(text: str) -> str:
    """Generate a short content hash for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def index_file(file_path: Path, root: Path) -> list[dict]:
    """Index a single file into one or more document chunks."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    if not content.strip():
        return []

    relative = str(file_path.relative_to(root)).replace("\\", "/")
    category = file_category(file_path)

    # Extract title from first heading
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    # Extract frontmatter name if present
    name_match = re.search(r"^name:\s+(.+)", content, re.MULTILINE)
    if name_match:
        title = name_match.group(1).strip().strip('"')

    chunks = chunk_text(content)
    documents = []

    for i, chunk in enumerate(chunks):
        doc_id = f"{relative}:{i}" if len(chunks) > 1 else relative
        documents.append({
            "id": content_hash(doc_id),
            "source": relative,
            "title": title,
            "category": category,
            "chunk_index": i,
            "chunk_total": len(chunks),
            "content": chunk,
            "content_length": len(chunk),
            "access_level": "internal",  # all platform docs are internal by default
        })

    return documents


def index_all(root: Path) -> list[dict]:
    """Index all content in the platform repository."""
    all_docs = []

    for file_path in sorted(root.rglob("*")):
        # Skip directories and non-indexable files
        if file_path.is_dir():
            continue
        if file_path.suffix not in INDEXABLE_EXTENSIONS:
            continue
        # Skip directories we don't want to index
        if any(skip in file_path.parts for skip in SKIP_DIRECTORIES):
            continue

        docs = index_file(file_path, root)
        all_docs.extend(docs)

    return all_docs


def main() -> int:
    args = sys.argv[1:]
    root_path = Path(".")
    output_file = None

    i = 0
    while i < len(args):
        if args[i] == "--root" and i + 1 < len(args):
            root_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if not root_path.exists():
        print(f"ERROR: Root path not found: {root_path}", file=sys.stderr)
        return 1

    print(f"Indexing content in: {root_path}", file=sys.stderr)
    documents = index_all(root_path)

    # Summary
    categories: dict[str, int] = {}
    for doc in documents:
        cat = doc["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print(f"Indexed {len(documents)} document chunks:", file=sys.stderr)
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}", file=sys.stderr)

    output = json.dumps(documents, indent=2)

    if output_file:
        output_file.write_text(output, encoding="utf-8")
        print(f"Written to: {output_file}", file=sys.stderr)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())