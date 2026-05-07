#!/usr/bin/env python3
"""
scaffold_missing_skill.py — Scaffold a new skill directory and SKILL.md stub.

Creates the correct directory structure and a frontmatter-compliant SKILL.md
stub for a new skill, ready for human completion.

Usage:
    python scripts/skills/scaffold_missing_skill.py <skill-name> [--category core|sdlc] [--description "..."]

Example:
    python scripts/skills/scaffold_missing_skill.py my-new-skill --category sdlc
    python scripts/skills/scaffold_missing_skill.py my-core-skill --category core --description "Does X"
"""

import re
import sys
from pathlib import Path


SKILL_TEMPLATE = """\
---
name: {name}
description: {description}
metadata:
  version: "0.1.0"
  category: {category}
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management]
---

# {title}

## Role

<!-- TODO: Describe what this skill does, its purpose, and how it differs from other skills. -->

You are the {title} skill. [Describe the role here.]

---

## When This Skill Activates

Load this skill when:

- <!-- TODO: Add specific trigger condition 1 -->
- <!-- TODO: Add specific trigger condition 2 -->
- <!-- TODO: Add specific trigger condition 3 -->

---

## Execution Protocol

**Step 1 — [Step name]**
<!-- TODO: Describe what to do in this step, how to do it, and what to produce. -->

**Step 2 — [Step name]**
<!-- TODO: -->

**Step 3 — [Step name]**
<!-- TODO: -->

---

## References

<!-- TODO: Add references to supporting documents once created. -->
<!-- Example: - `references/my-template.md` — Description of what this file contains -->
"""


def to_kebab(name: str) -> str:
    """Normalize to kebab-case."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def to_title(name: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in name.split("-"))


def scaffold_skill(
    name: str,
    category: str = "sdlc",
    description: str = "",
    root: Path = Path("."),
) -> Path:
    """Create skill directory and SKILL.md stub. Returns the created file path."""
    name = to_kebab(name)
    title = to_title(name)

    if category == "core":
        skill_dir = root / "core" / name
    else:
        skill_dir = root / "skills" / name

    if skill_dir.exists():
        print(f"WARNING: Directory already exists: {skill_dir}")
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            print(f"ERROR: SKILL.md already exists at {skill_md}. Aborting.")
            sys.exit(1)
    else:
        skill_dir.mkdir(parents=True)
        print(f"Created: {skill_dir}/")

    # Create references subdirectory
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    print(f"Created: {refs_dir}/")

    if not description:
        description = f"[TODO: Add a concise description of the {title} skill — max 1024 chars]"

    content = SKILL_TEMPLATE.format(
        name=name,
        title=title,
        category=category,
        description=description,
    )

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(content, encoding="utf-8")
    print(f"Created: {skill_md}")

    return skill_md


def main() -> int:
    args = sys.argv[1:]

    if not args or args[0].startswith("--"):
        print("Usage: scaffold_missing_skill.py <skill-name> [--category core|sdlc] "
              "[--description '...'] [--root .]")
        print("Example: scaffold_missing_skill.py my-new-skill --category sdlc")
        return 1

    skill_name = args[0]
    category = "sdlc"
    description = ""
    root_path = Path(".")

    i = 1
    while i < len(args):
        if args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif args[i] == "--description" and i + 1 < len(args):
            description = args[i + 1]
            i += 2
        elif args[i] == "--root" and i + 1 < len(args):
            root_path = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if category not in ("core", "sdlc"):
        print(f"ERROR: --category must be 'core' or 'sdlc', got: {category}")
        return 1

    if not root_path.exists():
        print(f"ERROR: Root path not found: {root_path}")
        return 1

    skill_file = scaffold_skill(skill_name, category, description, root_path)
    print(f"\nScaffolded: {skill_file}")
    print("Next steps:")
    print("  1. Fill in the Role, Activation Triggers, and Execution Protocol sections")
    print("  2. Create reference files in the references/ subdirectory")
    print("  3. Run: python scripts/validation/validate_frontmatter.py .")
    print("  4. Run: python scripts/skills/detect_skill_gaps.py .")

    return 0


if __name__ == "__main__":
    sys.exit(main())