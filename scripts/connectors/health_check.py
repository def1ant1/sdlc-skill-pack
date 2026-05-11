#!/usr/bin/env python3
"""
health_check.py — Run health checks for all registered connectors.

Discovers connector classes dynamically from the connectors package and
calls health_check() on each, printing a status table.

Usage:
    python scripts/connectors/health_check.py
    python scripts/connectors/health_check.py --connector salesforce
    python scripts/connectors/health_check.py --json

Environment:
    All connector secrets must be available (Vault or env vars).
    Connectors that fail authentication are reported as UNREACHABLE.
"""
from __future__ import annotations

import importlib
import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "WARNING"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("health_check")

_HERE = Path(__file__).parent

# Map connector name → module.ClassName
CONNECTOR_REGISTRY: dict[str, tuple[str, str]] = {
    "salesforce": ("salesforce_connector", "SalesforceConnector"),
    "servicenow": ("servicenow_connector", "ServiceNowConnector"),
    "ga4": ("ga4_connector", "GA4Connector"),
    "slack": ("slack_connector", "SlackConnector"),
    "jira": ("jira_connector", "JiraConnector"),
    "hubspot": ("hubspot_connector", "HubSpotConnector"),
    "stripe": ("stripe_connector", "StripeConnector"),
    "mixpanel": ("mixpanel_connector", "MixpanelConnector"),
    "amplitude": ("amplitude_connector", "AmplitudeConnector"),
    "filesystem_local": ("local_apps.filesystem_connector", "FilesystemConnector"),
    "sqlite_local": ("local_apps.sqlite_connector", "SQLiteConnector"),
}


def check_connector(name: str, module_name: str, class_name: str) -> dict:
    """Instantiate a connector and run its health_check(). Return a result dict."""
    result = {
        "connector": name,
        "status": "UNKNOWN",
        "latency_ms": None,
        "error": None,
        "circuit_state": None,
        "read_only_default": None,
    }
    try:
        sys.path.insert(0, str(_HERE))
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        connector = cls()

        t0 = time.perf_counter()
        healthy = connector.health_check()
        latency_ms = int((time.perf_counter() - t0) * 1000)

        result["status"] = "OK" if healthy else "DEGRADED"
        result["latency_ms"] = latency_ms
        result["circuit_state"] = getattr(getattr(connector, "_circuit", None), "state", None)
        result["read_only_default"] = bool(getattr(connector, "_read_only_mode", False))
    except Exception as exc:
        result["status"] = "UNREACHABLE"
        result["error"] = str(exc)
        logger.debug("Connector %s failed: %s", name, exc, exc_info=True)

    return result


def run_checks(connector_filter: str | None = None) -> list[dict]:
    registry = CONNECTOR_REGISTRY
    if connector_filter:
        if connector_filter not in registry:
            raise ValueError(
                f"Unknown connector '{connector_filter}'. "
                f"Known: {', '.join(registry)}"
            )
        registry = {connector_filter: registry[connector_filter]}

    results = []
    for name, (mod, cls) in registry.items():
        logger.info("Checking connector: %s", name)
        results.append(check_connector(name, mod, cls))
    return results


def print_table(results: list[dict]) -> None:
    """Print a human-readable status table."""
    col_w = [16, 12, 12, 50]
    header = ["Connector", "Status", "Latency", "Error"]
    sep = "  ".join("-" * w for w in col_w)
    row_fmt = "  ".join(f"{{:<{w}}}" for w in col_w)

    print(row_fmt.format(*header))
    print(sep)
    for r in results:
        latency = f"{r['latency_ms']}ms" if r["latency_ms"] is not None else "-"
        error = (r["error"] or "")[:46]
        print(row_fmt.format(r["connector"], r["status"], latency, error))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Apotheon connector health checks")
    parser.add_argument("--connector", help="Check a single connector by name")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    args = parser.parse_args()

    try:
        results = run_checks(args.connector)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        print_table(results)

    # Exit 1 if any connector is not OK
    return 0 if all(r["status"] == "OK" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())