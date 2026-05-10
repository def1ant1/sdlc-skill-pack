#!/usr/bin/env python3
from __future__ import annotations

import hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md"
ROADMAP = ROOT / "ROADMAP.md"
DOCS = sorted((ROOT / "docs").rglob("*.md"))
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

def normalize(text:str)->str:
    return re.sub(r"\s+"," ",text.strip().lower())

def fingerprint(text:str)->str:
    return hashlib.sha256(normalize(text).encode()).hexdigest()[:16]

def sections_for(path:Path):
    lines=path.read_text(encoding="utf-8").splitlines(); out=[]; title=None; start=1; buf=[]
    for i,line in enumerate(lines,1):
        m=HEADING_RE.match(line)
        if m:
            if title is not None: out.append((title,"\n".join(buf).strip(),start))
            title=m.group(2).strip(); start=i; buf=[]
        elif title is not None: buf.append(line)
    if title is not None: out.append((title,"\n".join(buf).strip(),start))
    return out

def main()->int:
    sources=[BACKLOG,ROADMAP]
    for p in sources+DOCS:
        if not p.exists():
            print(f"Missing documentation target: {p.relative_to(ROOT)}"); return 1

    source_titles, source_bodies = {}, {}
    for src in sources:
        rel=src.relative_to(ROOT)
        for title,body,line in sections_for(src):
            source_titles.setdefault(normalize(title),[]).append(f"{rel}:{line} ({title})")
            if len(normalize(body))>=80:
                source_bodies.setdefault(fingerprint(body),[]).append(f"{rel}:{line} ({title})")

    generic={"capabilities","overview","purpose","requirements"}
    problems=0
    for doc in DOCS:
        rel=doc.relative_to(ROOT)
        for title,body,line in sections_for(doc):
            k=normalize(title)
            if k in generic:
                continue
            if k in source_titles:
                problems+=1
                print('Duplicate section title between canonical planning docs and docs/:')
                for r in source_titles[k]: print(f' - {r}')
                print(f' - {rel}:{line} ({title})')
            if len(normalize(body))>=80:
                b=fingerprint(body)
                if b in source_bodies:
                    problems+=1
                    print('Duplicate content fingerprint between canonical planning docs and docs/:')
                    for r in source_bodies[b]: print(f' - {r}')
                    print(f' - {rel}:{line} ({title})')
    if problems:
        print(f"\nFound {problems} duplication issue(s).")
        return 1
    print('No duplicate section titles/content fingerprints across backlog/roadmap and docs/.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
