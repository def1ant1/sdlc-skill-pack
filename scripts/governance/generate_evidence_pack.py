from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REGULATED_KEYWORDS = {"financial", "legal", "tax", "hr", "trading", "security", "logistics", "materials"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_regulated(payload: dict[str, Any]) -> bool:
    tags = payload.get("workflow_tags", [])
    if not isinstance(tags, list):
        return False
    lowered = {str(t).lower() for t in tags}
    return any(k in lowered for k in REGULATED_KEYWORDS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate auditable evidence packs for regulated workflows.")
    parser.add_argument("--workflow", type=Path, required=True, help="Workflow execution JSON payload")
    parser.add_argument("--decision-log", type=Path, required=True, help="Policy decision JSON emitted by enforce_runtime_policy")
    parser.add_argument("--output", type=Path, required=True, help="Path to write evidence pack JSON")
    args = parser.parse_args()

    workflow = _read_json(args.workflow)
    decision = _read_json(args.decision_log)

    if not _is_regulated(workflow):
        print("SKIP: workflow not classified as regulated")
        return 0

    evidence = {
        "generated_at": datetime.now(UTC).isoformat(),
        "workflow_id": workflow.get("workflow_id"),
        "workflow_tags": workflow.get("workflow_tags", []),
        "skill_path": workflow.get("skill_path"),
        "requested_actions": workflow.get("requested_actions", []),
        "approval_id": workflow.get("approval_id"),
        "policy_decision": decision,
        "audit_summary": {
            "status": decision.get("status"),
            "fail_closed": decision.get("status") == "deny",
            "violations": decision.get("violations", []),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: evidence pack written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
