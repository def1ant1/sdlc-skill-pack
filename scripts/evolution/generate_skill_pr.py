#!/usr/bin/env python3
"""Render a PR-ready markdown from evolution proposals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    lines = [
        "# Evolution Proposal Draft",
        "",
        "## Safety Gates",
        "- Auto-apply: **Disabled**",
        "- Auto-merge: **Disabled**",
        "- Human approval: **Required**",
        "",
        "## Suggested Changes",
    ]
    for idx, item in enumerate(proposal.get("proposals", []), start=1):
        lines.extend(
            [
                f"### {idx}. {item['workflow']} -> {item['skill']}",
                f"- Failure: {item['failure_reason']}",
                f"- Patch target: `{item['suggested_patch']['target_file']}`",
                f"- Change: {item['suggested_patch']['change_summary']}",
                f"- Risk: **{item['risk_level']}**",
                f"- Tests: `{'; '.join(item['suggested_tests'])}`",
                f"- Evals: `{'; '.join(item['suggested_evals'])}`",
                "",
            ]
        )
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
