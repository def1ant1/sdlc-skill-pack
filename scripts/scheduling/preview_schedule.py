#!/usr/bin/env python3
"""Preview deterministic next-run windows for schedule registry entries."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "schedules" / "registry.yaml"


def _parse_iso(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _weekday_matches(field: str, candidate: dt.datetime) -> bool:
    if field == "*":
        return True
    py_weekday = (candidate.weekday() + 1) % 7
    for token in field.split(","):
        if "-" in token:
            start, end = (int(p) for p in token.split("-", 1))
            if start <= py_weekday <= end:
                return True
        elif int(token) == py_weekday:
            return True
    return False


def _cron_matches(expr: str, candidate: dt.datetime) -> bool:
    minute, hour, dom, month, dow = expr.split()
    checks = [
        (minute, candidate.minute),
        (hour, candidate.hour),
        (dom, candidate.day),
        (month, candidate.month),
    ]
    for field, actual in checks:
        if field != "*" and int(field) != actual:
            return False
    return _weekday_matches(dow, candidate)


def _next_cron_runs(expr: str, as_of: dt.datetime, limit: int) -> list[dt.datetime]:
    runs: list[dt.datetime] = []
    probe = as_of.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
    max_probe = probe + dt.timedelta(days=31)
    while probe <= max_probe and len(runs) < limit:
        if _cron_matches(expr, probe):
            runs.append(probe)
        probe += dt.timedelta(minutes=1)
    return runs


def compute_due_runs(schedule: dict[str, Any], as_of: dt.datetime, lookback_minutes: int = 60) -> list[dt.datetime]:
    window_start = as_of - dt.timedelta(minutes=lookback_minutes)
    mode = schedule["mode"]
    if mode == "event":
        return []
    if mode == "interval":
        interval = int(schedule["interval_minutes"])
        anchor = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
        elapsed = int((window_start - anchor).total_seconds() // 60)
        first = anchor + dt.timedelta(minutes=(elapsed // interval) * interval)
        if first < window_start:
            first += dt.timedelta(minutes=interval)
        runs: list[dt.datetime] = []
        while first <= as_of:
            runs.append(first)
            first += dt.timedelta(minutes=interval)
        return runs
    expr = schedule["cron"]
    return [r for r in _next_cron_runs(expr, window_start - dt.timedelta(minutes=1), 500) if r <= as_of]


def load_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    payload = yaml.safe_load(path.read_text())
    return payload.get("schedules", [])


def preview(path: Path, as_of: dt.datetime, horizon_count: int) -> dict[str, Any]:
    schedules = load_registry(path)
    out: dict[str, Any] = {"as_of": as_of.isoformat(), "schedules": []}
    for sch in schedules:
        if not sch.get("enabled", False):
            continue
        mode = sch["mode"]
        if mode == "event":
            next_runs: list[str] = []
        elif mode == "interval":
            interval = int(sch["interval_minutes"])
            next_runs = [(as_of + dt.timedelta(minutes=interval * (i + 1))).isoformat() for i in range(horizon_count)]
        else:
            next_runs = [r.isoformat() for r in _next_cron_runs(sch["cron"], as_of, horizon_count)]
        out["schedules"].append({"schedule_id": sch["schedule_id"], "mode": mode, "next_runs": next_runs})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).isoformat())
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    as_of = _parse_iso(args.as_of)
    result = preview(args.registry, as_of, args.count)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
