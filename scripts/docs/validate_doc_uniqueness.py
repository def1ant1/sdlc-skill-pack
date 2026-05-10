#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
MIN_SECTION_CHARS = 400


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def fingerprint(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:20]


def sections_for(path: Path) -> list[tuple[str, str, int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, str, int]] = []
    title: str | None = None
    start_line = 1
    body: list[str] = []

    for i, line in enumerate(lines, start=1):
        m = HEADING_RE.match(line)
        if m:
            if title is not None:
                sections.append((title, "\n".join(body).strip(), start_line))
            title = m.group(2).strip()
            start_line = i
            body = []
        elif title is not None:
            body.append(line)

    if title is not None:
        sections.append((title, "\n".join(body).strip(), start_line))
    return sections


def target_files() -> list[Path]:
    top_level_md = sorted(ROOT.glob("*.md"))
    readme_files = [p for p in top_level_md if p.name.lower().startswith("readme")]
    backlog_files = [p for p in top_level_md if "backlog" in p.name.lower()]
    docs_top_level = sorted((ROOT / "docs").glob("*.md")) if (ROOT / "docs").exists() else []
    docs_governance = [ROOT / "docs/standards/documentation-governance.md"]

    files = sorted({*readme_files, *backlog_files, *docs_top_level, *docs_governance})
    return [p for p in files if p.exists()]


def main() -> int:
    files = target_files()
    if not files:
        print("No target files found for uniqueness validation.")
        return 0

    buckets: dict[str, list[str]] = {}
    for file_path in files:
        rel = file_path.relative_to(ROOT)
        for title, body, line in sections_for(file_path):
            body_norm = normalize(body)
            if len(body_norm) < MIN_SECTION_CHARS:
                continue
            key = fingerprint(body)
            buckets.setdefault(key, []).append(f"{rel}:{line} ({title})")

    duplicates = {k: v for k, v in buckets.items() if len(v) > 1}
    if duplicates:
        print("Duplicate large documentation sections detected:")
        for _, refs in sorted(duplicates.items(), key=lambda kv: kv[1][0]):
            for ref in refs:
                print(f" - {ref}")
            print()
        print(f"Found {len(duplicates)} duplicated section fingerprint(s).")
        return 1

    print("No duplicate large sections across top-level backlog/docs/readme files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
