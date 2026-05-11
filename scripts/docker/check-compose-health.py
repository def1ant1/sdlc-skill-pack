#!/usr/bin/env python3
import json
import subprocess
import sys

SERVICES = ["apotheon-postgres", "apotheon-redis", "apotheon-qdrant", "apotheon-temporal", "apotheon-runtime"]

results = {}
failed = False
for service in SERVICES:
    cmd = ["docker", "inspect", "--format", "{{json .State.Health}}", service]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        results[service] = {"status": "missing"}
        failed = True
        continue
    health = json.loads(proc.stdout.strip()) if proc.stdout.strip() else {}
    status = health.get("Status", "none")
    results[service] = {"status": status}
    if status not in {"healthy", "none"}:
        failed = True

print(json.dumps(results, indent=2))
sys.exit(1 if failed else 0)
