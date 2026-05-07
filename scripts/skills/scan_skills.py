#!/usr/bin/env python3
"""
scan_skills.py — Scan all SKILL.md files and produce a skill capability map.

Usage:
    python scripts/skills/scan_skills.py [--output json|table] [--root .]

Output: JSON map of skill name → {path, description, maturity, dependencies, sections}
"""

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter fields from SKILL.md content."""
    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter_text = content[3:end].strip()
    result = {}

    # Simple key-value extraction (avoids full YAML dependency)
    current_key = None
    in_metadata = False
    in_dependencies = False
    deps = []

    for line in frontmatter_text.splitlines():
        if line.strip() == "metadata:":
            in_metadata = True
            continue

        if in_dependencies:
            dep_match = re.match(r"\s*-\s+(.+)", line)
            if dep_match:
                deps.append(dep_match.group(1).strip())
                continue
            else:
                in_dependencies = False
                result["dependencies"] = deps
                deps = []

        if in_metadata:
            meta_match = re.match(r"\s{2}(\w+):\s*(.+)", line)
            if meta_match:
                key, value = meta_match.group(1), meta_match.group(2).strip().strip('"')
                if key == "dependencies":
                    # inline list: [a, b, c]
                    if "[" in value:
                        items = value.strip("[]").split(",")
                        result["dependencies"] = [i.strip() for i in items if i.strip()]
                    else:
                        in_dependencies = True
                        deps = []
                else:
                    result[key] = value
            elif re.match(r"\s{2}dependencies:", line):
                in_dependencies = True
        else:
            kv_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
            if kv_match:
                key, value = kv_match.group(1), kv_match.group(2).strip().strip('"')
                result[key] = value

    if deps:
        result["dependencies"] = deps

    return result


def extract_sections(content: str) -> list[str]:
    """Extract top-level section headers from SKILL.md body."""
    sections = []
    in_body = False
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if not in_body:
            if line.strip() == "---" and i > 0:
                in_body = True
            continue
        if line.startswith("## "):
            sections.append(line[3:].strip())

    return sections


def extract_references(content: str) -> list[str]:
    """Extract referenced file paths from the References section."""
    refs = []
    in_refs = False
    for line in content.splitlines():
        if line.startswith("## References"):
            in_refs = True
            continue
        if in_refs:
            if line.startswith("## "):
                break
            ref_match = re.search(r"`(references/[^`]+)`", line)
            if ref_match:
                refs.append(ref_match.group(1))
    return refs


def scan_skills(root: Path) -> dict:
    """Scan all SKILL.md files and build capability map."""
    skill_map = {}

    for skill_file in sorted(root.glob("**/SKILL.md")):
        # Skip test fixtures and template files
        if "test" in str(skill_file) or "template" in str(skill_file):
            continue

        content = skill_file.read_text(encoding="utf-8", errors="replace")
        frontmatter = parse_frontmatter(content)
        sections = extract_sections(content)
        references = extract_references(content)

        name = frontmatter.get("name", skill_file.parent.name)
        relative_path = str(skill_file.relative_to(root)).replace("\\", "/")

        skill_map[name] = {
            "path": relative_path,
            "description": frontmatter.get("description", ""),
            "version": frontmatter.get("version", "unknown"),
            "category": frontmatter.get("category", "unknown"),
            "maturity": frontmatter.get("maturity", "unknown"),
            "dependencies": frontmatter.get("dependencies", []),
            "sections": sections,
            "references": references,
            "line_count": len(content.splitlines()),
        }

    return skill_map


def print_table(skill_map: dict) -> None:
    """Print a human-readable summary table."""
    print(f"\n{'SKILL REGISTRY':=<70}")
    print(f"{'Name':<35} {'Maturity':<10} {'Category':<12} {'Sections'}")
    print("-" * 70)
    for name, info in sorted(skill_map.items()):
        sections_count = len(info["sections"])
        print(
            f"{name:<35} {info['maturity']:<10} {info['category']:<12} {sections_count} sections"
        )
    print(f"\nTotal skills: {len(skill_map)}")


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

    skill_map = scan_skills(root_path)

    if output_format == "json":
        print(json.dumps(skill_map, indent=2))
    else:
        print_table(skill_map)

    return 0


if __name__ == "__main__":
    sys.exit(main())