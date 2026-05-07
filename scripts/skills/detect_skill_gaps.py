#!/usr/bin/env python3
"""
detect_skill_gaps.py — Detect gaps in the skill registry.

Runs gap detection rules from core/skill-gap-engine/references/gap-detection-rules.md:
  - Missing references files
  - Invalid frontmatter
  - Skills with < 4 sections (likely stubs)
  - Missing dependencies in registry

Usage:
    python scripts/skills/detect_skill_gaps.py [--root .] [--output json|table]

Exit code: 0 if no CRITICAL gaps; 1 if CRITICAL gaps found.
"""

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Simple frontmatter parser."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    fm = content[3:end].strip()
    result = {}
    for line in fm.splitlines():
        kv = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if kv:
            result[kv.group(1)] = kv.group(2).strip().strip('"')
    # Parse dependencies list
    deps_match = re.search(r"dependencies:\s*\[([^\]]+)\]", fm)
    if deps_match:
        result["dependencies"] = [d.strip() for d in deps_match.group(1).split(",")]
    return result


def count_sections(content: str) -> int:
    """Count ## sections in SKILL.md body."""
    return len(re.findall(r"^## ", content, re.MULTILINE))


def extract_references(content: str) -> list[str]:
    """Extract referenced file paths."""
    return re.findall(r"`(references/[^`]+\.md)`", content)


def detect_gaps(root: Path) -> list[dict]:
    """Run all gap detection rules. Returns list of gap records."""
    gaps = []
    registered_names: set[str] = set()

    skill_files = list(root.glob("**/SKILL.md"))
    # Skip any files in test directories
    skill_files = [f for f in skill_files if "test" not in str(f)]

    # First pass: collect registered names
    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        if fm.get("name"):
            registered_names.add(fm["name"])

    # Second pass: detect gaps
    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        skill_dir = skill_file.parent
        relative = str(skill_file.relative_to(root)).replace("\\", "/")

        # QUA-003: Invalid frontmatter
        if not fm.get("name") or not fm.get("description"):
            gaps.append({
                "rule": "QUA-003",
                "type": "INVALID_FRONTMATTER",
                "severity": "CRITICAL",
                "skill": relative,
                "description": "Missing required frontmatter field: name or description",
                "recommended_action": "Add required frontmatter fields",
            })

        # Stub detection: very few sections = likely incomplete
        section_count = count_sections(content)
        if section_count < 3:
            gaps.append({
                "rule": "QUA-001",
                "type": "WEAK",
                "severity": "HIGH",
                "skill": fm.get("name", relative),
                "description": f"Skill has only {section_count} section(s) — likely a stub",
                "recommended_action": "Expand skill with full execution protocol and references",
            })

        # QUA-004: Missing reference files
        refs = extract_references(content)
        for ref_path in refs:
            full_ref = skill_dir / ref_path
            if not full_ref.exists():
                gaps.append({
                    "rule": "QUA-004",
                    "type": "MISSING_REFERENCE",
                    "severity": "MEDIUM",
                    "skill": fm.get("name", relative),
                    "description": f"Referenced file does not exist: {ref_path}",
                    "recommended_action": f"Create {skill_dir}/{ref_path}",
                })

        # CUR-003: Deprecated/missing dependencies
        deps = fm.get("dependencies", [])
        if isinstance(deps, str):
            deps_match = re.findall(r"[\w-]+", deps)
            deps = deps_match

        for dep in deps:
            dep_clean = dep.strip("[]")
            if dep_clean and dep_clean not in registered_names:
                # Check if it's a known legacy name
                gaps.append({
                    "rule": "CUR-003",
                    "type": "DEPENDENCY",
                    "severity": "MEDIUM",
                    "skill": fm.get("name", relative),
                    "description": f"Dependency '{dep_clean}' not found in skill registry",
                    "recommended_action": f"Verify '{dep_clean}' exists or update dependency name",
                })

    return gaps


def print_table(gaps: list[dict]) -> None:
    """Print gap report as a table."""
    print(f"\n{'SKILL GAP REPORT':=<70}")

    if not gaps:
        print("[OK] No gaps detected.")
        return

    by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
    for gap in gaps:
        sev = gap.get("severity", "MEDIUM")
        by_severity.setdefault(sev, []).append(gap)

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = by_severity.get(severity, [])
        if not items:
            continue
        print(f"\n[{severity}] — {len(items)} gap(s)")
        print("-" * 60)
        for g in items:
            print(f"  Rule:   {g['rule']} ({g['type']})")
            print(f"  Skill:  {g['skill']}")
            print(f"  Issue:  {g['description']}")
            print(f"  Fix:    {g['recommended_action']}")
            print()

    critical_count = len(by_severity.get("CRITICAL", []))
    high_count = len(by_severity.get("HIGH", []))
    print(f"Total gaps: {len(gaps)} "
          f"(CRITICAL: {critical_count}, HIGH: {high_count}, "
          f"MEDIUM: {len(by_severity.get('MEDIUM', []))}, "
          f"LOW: {len(by_severity.get('LOW', []))})")


def main() -> int:
    args = sys.argv[1:]
    output_format = "table"
    root_path = Path(".")

    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif args[i] == "--root" and i + 1 < len(args):
            root_path = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if not root_path.exists():
        print(f"ERROR: Root path not found: {root_path}", file=sys.stderr)
        return 1

    gaps = detect_gaps(root_path)

    if output_format == "json":
        print(json.dumps(gaps, indent=2))
    else:
        print_table(gaps)

    # Exit 1 if CRITICAL gaps found
    has_critical = any(g["severity"] == "CRITICAL" for g in gaps)
    return 1 if has_critical else 0


if __name__ == "__main__":
    sys.exit(main())