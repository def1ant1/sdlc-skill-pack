#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "schedules" / "registry.yaml"


def parse_iso(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _next_cron_runs(expr: str, as_of_local: dt.datetime, limit: int) -> list[dt.datetime]:
    runs=[]
    probe=as_of_local.replace(second=0,microsecond=0)+dt.timedelta(minutes=1)
    max_probe=probe+dt.timedelta(days=90)
    minute,hour,dom,month,dow=expr.split()
    def wk(tok,v):
        if tok=="*": return True
        return any((int(x.split("-")[0])<=v<=int(x.split("-")[1]) if "-" in x else int(x)==v) for x in tok.split(","))
    while probe<=max_probe and len(runs)<limit:
        pyw=(probe.weekday()+1)%7
        if wk(minute,probe.minute) and wk(hour,probe.hour) and wk(dom,probe.day) and wk(month,probe.month) and wk(dow,pyw):
            runs.append(probe)
        probe+=dt.timedelta(minutes=1)
    return runs


def load_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    payload = yaml.safe_load(path.read_text()) or {}
    return payload.get("schedules", [])


def compute_due_runs(schedule: dict[str, Any], as_of: dt.datetime, lookback_minutes: int = 60) -> list[dt.datetime]:
    window_start = as_of - dt.timedelta(minutes=lookback_minutes)
    mode = schedule["mode"]
    if mode in {"manual", "event"}:
        return []

    tz = ZoneInfo(schedule.get("timezone", "UTC"))
    if mode == "interval":
        interval = int(schedule["interval_minutes"])
        anchor = parse_iso(schedule.get("anchor_time", "1970-01-01T00:00:00Z"))
        elapsed = int((window_start - anchor).total_seconds() // 60)
        first = anchor + dt.timedelta(minutes=(elapsed // interval) * interval)
        if first < window_start:
            first += dt.timedelta(minutes=interval)
        runs: list[dt.datetime] = []
        while first <= as_of:
            runs.append(first.astimezone(dt.timezone.utc))
            first += dt.timedelta(minutes=interval)
        return runs

    expr = schedule["cron"]
    local_start = (window_start - dt.timedelta(minutes=1)).astimezone(tz)
    candidates = _next_cron_runs(expr, local_start, 512)
    return [c.astimezone(dt.timezone.utc) for c in candidates if c.astimezone(dt.timezone.utc) <= as_of]


def preview(path: Path, as_of: dt.datetime, horizon_count: int) -> dict[str, Any]:
    out: dict[str, Any] = {"as_of": as_of.isoformat(), "schedules": []}
    for sch in load_registry(path):
        if not sch.get("enabled", False):
            continue
        mode = sch["mode"]
        if mode in {"manual", "event"}:
            next_runs: list[str] = []
        elif mode == "interval":
            next_runs = [
                (as_of + dt.timedelta(minutes=int(sch["interval_minutes"]) * (i + 1))).isoformat()
                for i in range(horizon_count)
            ]
        else:
            tz = ZoneInfo(sch.get("timezone", "UTC"))
            next_runs = [d.astimezone(dt.timezone.utc).isoformat() for d in _next_cron_runs(sch["cron"], as_of.astimezone(tz), horizon_count)]
        out["schedules"].append({"schedule_id": sch["schedule_id"], "mode": mode, "next_runs": next_runs})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).isoformat())
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(preview(args.registry, parse_iso(args.as_of), args.count), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
