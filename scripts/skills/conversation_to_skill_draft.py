#!/usr/bin/env python3
"""Draft a reusable skill artifact from conversation text before any write/promotion action."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.skills.scaffold_missing_skill import SKILL_TEMPLATE, to_kebab, to_title



def _bullets(section: str) -> list[str]:
    return [line.strip("- ").strip() for line in section.splitlines() if line.strip().startswith("-")]


def _extract_sections(conversation: str) -> dict[str, list[str]]:
    lines = [ln.strip() for ln in conversation.splitlines() if ln.strip()]
    purpose = [ln for ln in lines if any(k in ln.lower() for k in ("goal", "purpose", "outcome"))][:3]
    boundaries = [ln for ln in lines if any(k in ln.lower() for k in ("must not", "do not", "boundary", "guardrail"))][:5]
    deps = [ln for ln in lines if any(k in ln.lower() for k in ("depend", "requires", "integrate", "use "))][:5]
    hitl = [ln for ln in lines if any(k in ln.lower() for k in ("approve", "approval", "review", "hitl", "human"))][:5]
    examples = [ln for ln in lines if ln.lower().startswith(("example", "input:", "output:"))][:6]
    return {
        "purpose": purpose,
        "boundaries": boundaries,
        "dependencies": deps,
        "hitl_gates": hitl,
        "examples": examples,
    }


def generate_skill_markdown(name: str, category: str, description: str, sections: dict[str, list[str]]) -> str:
    title = to_title(name)
    base = SKILL_TEMPLATE.format(name=name, title=title, category=category, description=description)
    enrichment = [
        "\n## Drafted Skill Contract\n",
        "### Purpose",
        *(f"- {x}" for x in (sections["purpose"] or ["Derived from source conversation."])),
        "\n### Inputs",
        "- Source conversation text",
        "- Optional plan/workflow artifact paths",
        "\n### Outputs",
        "- SKILL.md draft ready for human review",
        "- Provenance JSON draft",
        "\n### Boundaries",
        *(f"- {x}" for x in (sections["boundaries"] or ["No filesystem writes without explicit approval."])),
        "\n### Dependencies",
        *(f"- {x}" for x in (sections["dependencies"] or ["scripts/skills/scaffold_missing_skill.py"])),
        "\n### HITL Gates",
        *(f"- {x}" for x in (sections["hitl_gates"] or ["Require explicit --approve-write to persist files."])),
        "\n### Examples",
        *(f"- {x}" for x in (sections["examples"] or ["Example input: Build reusable skill for onboarding.", "Example output: Draft skill + provenance."])),
    ]
    return base + "\n" + "\n".join(enrichment) + "\n"


def run_validators(skill_md: str, name: str) -> list[str]:
    messages: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        cmds = [
            ["python", str(ROOT / "scripts/validation/validate_frontmatter.py"), str(root)],
            ["python", str(ROOT / "scripts/validation/validate_skill_structure.py"), str(root)],
        ]
        for cmd in cmds:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            ok = proc.returncode == 0
            messages.append(f"{'PASS' if ok else 'FAIL'} {' '.join(cmd[1:])}")
            if not ok:
                messages.append(proc.stdout.strip() or proc.stderr.strip())
    return messages


def main() -> int:
    p = argparse.ArgumentParser(description="Draft reusable skill artifact from conversation text")
    p.add_argument("--name", required=True)
    p.add_argument("--category", default="sdlc", choices=["sdlc", "core"])
    p.add_argument("--description", default="")
    p.add_argument("--conversation", default="")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--plan", action="append", default=[])
    p.add_argument("--workflow", action="append", default=[])
    p.add_argument("--approve-write", action="store_true")
    args = p.parse_args()

    conversation = args.conversation
    if args.stdin or not conversation:
        import sys
        conversation = sys.stdin.read().strip()

    skill_name = to_kebab(args.name)
    sections = _extract_sections(conversation)
    description = args.description or f"Reusable {to_title(skill_name)} skill drafted from conversation."
    skill_md = generate_skill_markdown(skill_name, args.category, description, sections)

    provenance = {
        "generated_at": datetime.now(UTC).isoformat(),
        "skill_name": skill_name,
        "source": {
            "conversation_excerpt": conversation[:2000],
            "plan_artifacts": args.plan,
            "workflow_artifacts": args.workflow,
        },
        "draft_sections": sections,
        "write_approved": bool(args.approve_write),
    }

    print("=== GENERATED SKILL ARTIFACT (REVIEW REQUIRED) ===")
    print(skill_md)
    print("=== PROVENANCE ===")
    print(json.dumps(provenance, indent=2))

    print("=== PRE-WRITE VALIDATION ===")
    for m in run_validators(skill_md, skill_name):
        print(m)

    if not args.approve_write:
        print("Write skipped: pass --approve-write after editing/review to persist files.")
        return 0

    skill_root = ROOT / ("core" if args.category == "core" else "skills") / skill_name
    skill_root.mkdir(parents=True, exist_ok=True)
    (skill_root / "references").mkdir(exist_ok=True)
    (skill_root / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (skill_root / "draft.provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote skill draft: {skill_root / 'SKILL.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
