#!/usr/bin/env python3
"""
Validate skill folder structure.

Checks:
  1. Folder names are kebab-case
  2. Every skill folder contains SKILL.md
  3. Progressive disclosure: SKILL.md files are within size limits

Size limits (excludes frontmatter block):
  core/  skills: warning at 300 lines, error at 500 lines
  skills/ domain: warning at 150 lines, error at 300 lines
"""
from pathlib import Path
import re, sys, json

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
errors = []
warnings = []

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Progressive disclosure thresholds (lines, excluding frontmatter)
THRESHOLDS = {
    "core":   {"warn": 300, "error": 500},
    "skills": {"warn": 150, "error": 300},
}


def count_content_lines(skill_md: Path) -> int:
    """Return line count of SKILL.md excluding the YAML frontmatter block."""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    # Strip leading frontmatter (--- ... ---)
    if lines and lines[0].strip() == "---":
        try:
            close = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
            lines = lines[close + 1:]
        except StopIteration:
            pass  # No closing ---; count everything
    return len(lines)


for tier in ["skills", "core"]:
    base = ROOT / tier
    if not base.exists():
        continue

    for p in base.iterdir():
        if not p.is_dir():
            continue

        # Check 1: kebab-case folder name
        if not NAME_RE.match(p.name):
            errors.append(f"invalid folder name: {p.relative_to(ROOT)}")

        # Check 2: SKILL.md must exist
        skill_md = p / "SKILL.md"
        if tier == "skills" and not skill_md.exists():
            errors.append(f"missing SKILL.md: {p.relative_to(ROOT)}")
            continue
        if tier == "core" and p.name in ("orchestration", "memory-token-management"):
            if not skill_md.exists():
                errors.append(f"missing SKILL.md: {p.relative_to(ROOT)}")
                continue

        # Check 3: progressive disclosure size check
        if skill_md.exists():
            content_lines = count_content_lines(skill_md)
            t = THRESHOLDS[tier]
            rel = skill_md.relative_to(ROOT)
            if content_lines > t["error"]:
                errors.append(
                    f"progressive-disclosure violation: {rel} has {content_lines} content lines "
                    f"(hard limit {t['error']}). Move detail to references/, templates/, or examples/."
                )
            elif content_lines > t["warn"]:
                warnings.append(
                    f"progressive-disclosure warning: {rel} has {content_lines} content lines "
                    f"(warning threshold {t['warn']}). Consider moving detail to references/."
                )

result = {"valid": not errors, "errors": errors, "warnings": warnings}
print(json.dumps(result, indent=2))
sys.exit(1 if errors else 0)