from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import yaml


REQUIRED_ENV = {
    "LOCAL_DB_NAME": "Set database name for local-db service.",
    "LOCAL_DB_USER": "Set database username for local-db service.",
    "LOCAL_DB_PASSWORD": "Set database password for local-db service.",
    "APP_DATABASE_URL": "Provide SQLAlchemy/DB connection string reachable from local-app.",
    "APP_QUEUE_URL": "Provide queue URL (e.g., redis://local-queue:6379/0).",
    "APP_API_KEY": "Provide API key for local-app auth/feature gates.",
    "WORKER_QUEUE_URL": "Provide worker queue URL matching queue service.",
}

@dataclass
class ServiceCheck:
    name: str
    container_running: bool
    container_health: str
    api_usable: bool
    api_message: str


def _load_env(path: Path) -> dict[str, str]:
    env = dict(os.environ)
    if path.exists():
        for line in path.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def _docker_inspect(service: str, compose_file: Path) -> dict[str, Any]:
    cmd = ["docker", "compose", "-f", str(compose_file), "ps", "--format", "json", service]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return {}
    try:
        return json.loads(result.stdout.strip().splitlines()[0])
    except json.JSONDecodeError:
        return {}


def _check_http(url: str) -> tuple[bool, str]:
    try:
        with urlopen(url, timeout=2) as resp:
            code = resp.getcode()
            return (200 <= code < 400, f"HTTP {code}")
    except URLError as err:
        return False, f"unreachable: {err}"


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def generate_health_report(compose_file: Path, env_file: Path) -> dict[str, Any]:
    compose = yaml.safe_load(compose_file.read_text())
    services = compose.get("services", {})
    env = _load_env(env_file)

    missing_env = [
        {
            "variable": k,
            "remediation": f"Missing {k}. {msg}",
        }
        for k, msg in REQUIRED_ENV.items()
        if not env.get(k)
    ]

    ports_seen: dict[int, str] = {}
    port_conflicts: list[dict[str, str | int]] = []
    volume_missing: list[dict[str, str]] = []
    startup_order_warnings: list[str] = []

    checks: list[ServiceCheck] = []
    for name, svc in services.items():
        inspect = _docker_inspect(name, compose_file)
        state = str(inspect.get("State", "")).lower()
        health = str(inspect.get("Health", "unknown")).lower() or "unknown"
        running = state == "running"

        api_usable = False
        api_msg = "no API check configured"
        if name in {"local-app", "local-api"}:
            host_port = 8080 if name == "local-app" else 8000
            api_usable, api_msg = _check_http(f"http://127.0.0.1:{host_port}")

        checks.append(ServiceCheck(name, running, health, api_usable, api_msg))

        for port_spec in svc.get("ports", []) or []:
            m = re.match(r"(\d+):", str(port_spec))
            if not m:
                continue
            host_port = int(m.group(1))
            if host_port in ports_seen:
                port_conflicts.append({"port": host_port, "services": f"{ports_seen[host_port]}, {name}"})
            ports_seen[host_port] = name
            if _port_in_use(host_port) and not running:
                port_conflicts.append({"port": host_port, "services": name, "reason": "host port already occupied"})

        for volume_spec in svc.get("volumes", []) or []:
            host_path = str(volume_spec).split(":", 1)[0]
            if host_path.startswith("."):
                full = (compose_file.parent / host_path).resolve()
                if not full.exists():
                    volume_missing.append({"service": name, "path": str(full)})

        for dep in (svc.get("depends_on") or {}).keys():
            dep_check = next((c for c in checks if c.name == dep), None)
            if dep_check and not dep_check.container_running:
                startup_order_warnings.append(f"{name} depends on {dep}, but {dep} is not running")

    backup_ready = any("/backups" in str(v) for s in services.values() for v in (s.get("volumes", []) or []))

    migration = env.get("APP_MIGRATION_LEVEL", "unknown")
    version = env.get("APP_VERSION", "unknown")
    target = env.get("APP_TARGET_VERSION", version)
    upgrade_warnings = []
    if migration != "current":
        upgrade_warnings.append("Migrations are not current; run migration before API usability validation.")
    if target != version:
        upgrade_warnings.append(f"Upgrade planned from {version} to {target}; verify compatibility and rollback path.")

    return {
        "env_validation": {"passed": len(missing_env) == 0, "missing": missing_env},
        "service_health": [c.__dict__ for c in checks],
        "startup_dependency_order": {"warnings": startup_order_warnings, "passed": len(startup_order_warnings) == 0},
        "port_conflicts": {"conflicts": port_conflicts, "passed": len(port_conflicts) == 0},
        "volume_existence": {"missing": volume_missing, "passed": len(volume_missing) == 0},
        "backup_readiness": {
            "ready": backup_ready,
            "remediation": "Mount a backup path (e.g., ./backups:/backups) and validate write permissions." if not backup_ready else "ok",
        },
        "upgrade_migration_warnings": upgrade_warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    report = generate_health_report(args.compose_file, args.env_file)
    text = json.dumps(report, indent=2)
    if args.output_json:
        args.output_json.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
