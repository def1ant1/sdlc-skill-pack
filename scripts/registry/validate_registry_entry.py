#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--index", default="skill_registry/skills.index.json")
    args = p.parse_args()
    index_path = Path(args.index)
    data = json.loads(index_path.read_text())
    skills = data.get("skills", [])
    seen = set()
    for i, entry in enumerate(skills):
      name = entry.get("skill", "")
      path = entry.get("path", "")
      ver = entry.get("version", "")
      if not re.match(r"^[a-z0-9-]+$", name):
          raise SystemExit(f"invalid skill name at index {i}: {name}")
      if name in seen:
          raise SystemExit(f"duplicate skill: {name}")
      seen.add(name)
      if not SEMVER.match(ver):
          raise SystemExit(f"invalid semver for {name}: {ver}")
      if not Path(path).exists():
          raise SystemExit(f"skill path missing for {name}: {path}")
    print(f"registry validation passed ({len(skills)} skills)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
