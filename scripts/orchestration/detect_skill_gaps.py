#!/usr/bin/env python3
"""
detect_skill_gaps.py — Detect missing skills and unresolved dependencies.

Scans the skills/ and core/ directories to:
  1. Build a registry of all skill names (from SKILL.md frontmatter)
  2. Parse dependency declarations in each skill's frontmatter
  3. Report skills listed as dependencies that have no corresponding directory

Usage:
    python scripts/orchestration/detect_skill_gaps.py
    python scripts/orchestration/detect_skill_gaps.py /path/to/repo
    python scripts/orchestration/detect_skill_gaps.py --json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("detect_skill_gaps")

# ---------------------------------------------------------------------------
# Known aliases: virtual skill names used in dependency declarations that
# intentionally have no corresponding SKILL.md on disk (e.g. orchestration
# scripts, connector hub, etc.)
# ---------------------------------------------------------------------------
_KNOWN_ALIASES: frozenset[str] = frozenset({
    "gtm-orchestration",
    "connector-hub",
    "telemetry",
    "sdlc-memory-token-management",
    "sdlc-orchestration",
})

# Directories (by path part name) that are never real skills
_EXCLUDED_PARTS: frozenset[str] = frozenset({"tests", "test", "__pycache__", ".git", "node_modules"})


def _find_skill_files(root: Path) -> list[Path]:
    """Return all SKILL.md paths under skills/ and core/, excluding test dirs."""
    skill_files: list[Path] = []
    for base_dir in ("skills", "core"):
        base = root / base_dir
        if not base.is_dir():
            continue
        for path in base.rglob("SKILL.md"):
            # Exclude any path whose parts contain a test/cache directory
            if any(part in _EXCLUDED_PARTS for part in path.parts):
                continue
            skill_files.append(path)
    return skill_files


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter as a dict (requires PyYAML)."""
    try:
        import yaml
    except ImportError:
        return {}

    if not text.startswith("---"):
        return {}
    try:
        end = text.index("---", 3)
    except ValueError:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}


def _kebab(name: str) -> str:
    return name.lower().replace("_", "-").strip()


def detect_gaps(repo_root: Path) -> dict:
    """
    Scan repo for skill gaps.

    Returns:
        {
          "registered_skills": ["skill-a", ...],
          "missing_skills": [],             # reserved for future use
          "missing_dependencies": ["dep-x", ...]
        }
    """
    skill_files = _find_skill_files(repo_root)

    # Build registry from directory names (not frontmatter names, to be fast)
    registered_names: set[str] = set()
    for path in skill_files:
        dir_name = path.parent.name
        registered_names.add(_kebab(dir_name))

    # Collect all declared dependencies
    all_deps: set[str] = set()
    for path in skill_files:
        fm = _parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        meta = fm.get("metadata", {}) or {}
        deps = meta.get("dependencies", []) or []
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str):
                    all_deps.add(_kebab(dep))

    # Find dependencies that are neither registered skills nor known aliases
    missing_deps = sorted(
        dep for dep in all_deps
        if dep and dep not in registered_names and dep not in _KNOWN_ALIASES
    )

    return {
        "registered_skills": sorted(registered_names),
        "missing_skills": [],
        "missing_dependencies": missing_deps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect missing Apotheon skill dependencies")
    parser.add_argument("root", nargs="?", default=".", help="Repo root (default: .)")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    try:
        result = detect_gaps(repo_root)
        print(json.dumps(result, indent=2))

        if result["missing_dependencies"]:
            logger.warning(
                "%d unresolved dependencies: %s",
                len(result["missing_dependencies"]),
                result["missing_dependencies"],
            )
        return 0
    except Exception as exc:
        logger.error("detect_skill_gaps failed: %s", exc, exc_info=True)
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())