from __future__ import annotations

import datetime as dt
import json

from scripts.runtime.promote_schedule_to_temporal import promote_due_schedules


def _utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def _write_valid_plan(path):
    path.write_text(
        json.dumps(
            {
                "plan_id": "BUSINESS-20260511-abcd1234",
                "objective": "test objective",
                "planner": "business-workflow-planner",
                "planning_contract": {"schema": "workflow-plan@1.0", "version": "1.0"},
                "skill_chain": [{"step": 1, "skill": "finance-operations", "phase": "finance", "depends_on": []}],
            }
        )
    )


def test_promotion_payload_preserves_metadata_and_promotes(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: metadata-check
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_business_workflow.py
    risk_tier: high
    metadata:
      governance_tags: [sox, pci]
      lineage_ids: [lin-001, lin-002]
      description: metadata carryover test
""".strip()
    )
    plan = tmp_path / "plan.json"
    _write_valid_plan(plan)

    result = promote_due_schedules(
        _utc("2026-01-05T12:00:00Z"),
        registry,
        plan,
        tmp_path / "promotions",
        lookback_minutes=60,
        dry_run=False,
    )

    assert result["valid"] is True
    assert result["validation_errors"] == []
    assert {r["status"] for r in result["promotions"]} == {"promoted"}
    payload_path = tmp_path / "promotions" / "metadata-check" / "20260105T120000Z.json"
    payload = json.loads(payload_path.read_text())
    assert payload["metadata"]["owner"] == "ops"
    assert payload["metadata"]["risk_tier"] == "high"
    assert payload["metadata"]["governance_tags"] == ["sox", "pci"]
    assert payload["metadata"]["lineage_ids"] == ["lin-001", "lin-002"]


def test_dry_run_does_not_write_files_and_reports_payload(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: dryrun
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_business_workflow.py
    risk_tier: medium
""".strip()
    )
    plan = tmp_path / "plan.json"
    _write_valid_plan(plan)

    result = promote_due_schedules(_utc("2026-01-05T12:00:00Z"), registry, plan, tmp_path / "promotions", dry_run=True)
    assert result["valid"] is True
    assert result["promotions"]
    assert result["promotions"][0]["status"] == "dry_run"
    assert not (tmp_path / "promotions" / "dryrun").exists()


def test_validation_failure_for_contract_mismatch(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: bad-contract
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_gtm_workflow.py
    risk_tier: medium
""".strip()
    )
    bad_plan = tmp_path / "bad-plan.json"
    bad_plan.write_text(json.dumps({"plan_id": "X", "objective": "oops", "planner": "finance-workflow-planner", "planning_contract": {"schema": "wrong"}, "skill_chain": []}))

    result = promote_due_schedules(_utc("2026-01-05T12:00:00Z"), registry, bad_plan, tmp_path / "promotions")

    assert result["valid"] is False
    assert any("planning_contract.schema" in err for err in result["validation_errors"])
    assert any("does not align" in err for err in result["validation_errors"])
    assert result["promotions"] == []
