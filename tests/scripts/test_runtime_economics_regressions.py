import json
import subprocess
from pathlib import Path


def test_budget_compliance_and_rollup_ranking(tmp_path: Path):
    events = [
        {"event_category": "runtime", "correlation_id": "corr-1", "tenant_id": "t1", "cost_usd": 15, "workflow_id": "w1"},
        {"event_category": "runtime", "correlation_id": "corr-2", "tenant_id": "t1", "cost_usd": 20, "workflow_id": "w2"},
        {"event_category": "business", "correlation_id": "corr-1", "tenant_id": "t1", "value_usd": 120, "workflow_id": "w1"},
        {"event_category": "business", "correlation_id": "corr-2", "tenant_id": "t1", "value_usd": 80, "workflow_id": "w2"}
    ]
    p = tmp_path / "events.json"
    p.write_text(json.dumps(events), encoding="utf-8")

    ok = subprocess.run(["python", "scripts/validate_telemetry_events.py", str(p)], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr

    total_cost = sum(e.get("cost_usd", 0) for e in events)
    budget = 50
    assert total_cost <= budget  # budget compliance

    by_workflow = {}
    for e in events:
        wf = e["workflow_id"]
        by_workflow.setdefault(wf, {"cost": 0, "value": 0})
        by_workflow[wf]["cost"] += e.get("cost_usd", 0)
        by_workflow[wf]["value"] += e.get("value_usd", 0)

    ranked = sorted(
        ((wf, v["value"] / v["cost"]) for wf, v in by_workflow.items() if v["cost"] > 0),
        key=lambda x: x[1],
        reverse=True,
    )
    assert ranked[0][0] == "w1"  # value-to-cost ranking output
