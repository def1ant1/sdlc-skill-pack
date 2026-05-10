import json
import subprocess
from pathlib import Path


def test_budget_compliance_and_rollup_ranking(tmp_path: Path):
    events = [
        {
            "event_category": "runtime",
            "correlation_id": "corr-1",
            "tenant_id": "t1",
            "workflow_id": "w1",
            "skill_id": "token-cost-analysis",
            "agent_id": "analytics-agent",
            "domain": "economics",
            "cost_usd": 15,
        },
        {
            "event_category": "runtime",
            "correlation_id": "corr-2",
            "tenant_id": "t1",
            "workflow_id": "w2",
            "skill_id": "roi-estimation",
            "agent_id": "cfo-agent",
            "domain": "finance",
            "cost_usd": 20,
        },
        {
            "event_category": "business",
            "correlation_id": "corr-1",
            "tenant_id": "t1",
            "workflow_id": "w1",
            "skill_id": "token-cost-analysis",
            "agent_id": "analytics-agent",
            "domain": "economics",
            "value_usd": 120,
        },
        {
            "event_category": "business",
            "correlation_id": "corr-2",
            "tenant_id": "t1",
            "workflow_id": "w2",
            "skill_id": "roi-estimation",
            "agent_id": "cfo-agent",
            "domain": "finance",
            "value_usd": 80,
        },
    ]
    p = tmp_path / "events.json"
    p.write_text(json.dumps(events), encoding="utf-8")

    ok = subprocess.run(["python", "scripts/validate_telemetry_events.py", str(p)], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr

    total_cost = sum(e.get("cost_usd", 0) for e in events)
    budget = 50
    assert total_cost <= budget

    def rollup(dim: str):
        table = {}
        for event in events:
            key = event[dim]
            table.setdefault(key, {"cost": 0.0, "value": 0.0})
            table[key]["cost"] += float(event.get("cost_usd", 0))
            table[key]["value"] += float(event.get("value_usd", 0))
        return table

    for dimension in ("skill_id", "workflow_id", "agent_id", "tenant_id", "domain"):
        grouped = rollup(dimension)
        assert grouped
        ratios = {
            item_id: (vals["value"] / vals["cost"] if vals["cost"] > 0 else 0)
            for item_id, vals in grouped.items()
        }
        assert max(ratios.values()) > 0


def test_correlation_id_consistency_rejects_tenant_or_workflow_mismatch(tmp_path: Path):
    invalid_events = [
        {"event_category": "runtime", "correlation_id": "corr-x", "tenant_id": "t1", "workflow_id": "w1", "cost_usd": 1},
        {"event_category": "business", "correlation_id": "corr-x", "tenant_id": "t2", "workflow_id": "w2", "value_usd": 2},
    ]
    p = tmp_path / "bad_events.json"
    p.write_text(json.dumps(invalid_events), encoding="utf-8")

    fail = subprocess.run(["python", "scripts/validate_telemetry_events.py", str(p)], capture_output=True, text=True)
    assert fail.returncode == 1
    assert "tenant_id mismatch" in fail.stdout
    assert "workflow_id mismatch" in fail.stdout
