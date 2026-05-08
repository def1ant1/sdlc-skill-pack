#!/usr/bin/env python3
"""
init_temporal_namespace.py — Create or verify the Apotheon Temporal namespace.

Idempotent: safe to run on an already-configured cluster.

Usage:
    python scripts/runtime/init_temporal_namespace.py
    python scripts/runtime/init_temporal_namespace.py --namespace apotheon-prod --retention 30

Environment variables:
    TEMPORAL_HOST        Temporal server (default: localhost:7233)
    TEMPORAL_NAMESPACE   Namespace to create (default: apotheon-dev)
    RETENTION_DAYS       Workflow history retention (default: 7)
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("init_temporal_namespace")

TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))


async def ensure_namespace(host: str, namespace: str, retention_days: int) -> str:
    """Create namespace if it does not exist. Returns 'created' or 'exists'."""
    try:
        from temporalio.client import Client
        from temporalio.service import RPCError
    except ImportError:
        raise RuntimeError("temporalio package not installed. Run: pip install temporalio")

    client = await Client.connect(host)
    service = client.workflow_service

    # Try to describe — if it succeeds the namespace already exists
    try:
        from temporalio.api.workflowservice.v1 import DescribeNamespaceRequest
        await service.describe_namespace(DescribeNamespaceRequest(namespace=namespace))
        logger.info("Namespace '%s' already exists — skipping creation", namespace)
        return "exists"
    except Exception:
        pass  # Namespace not found — create it

    try:
        from temporalio.api.workflowservice.v1 import RegisterNamespaceRequest
        from temporalio.api.enums.v1 import ArchivalState
        from google.protobuf.duration_pb2 import Duration

        retention = Duration(seconds=retention_days * 86400)
        req = RegisterNamespaceRequest(
            namespace=namespace,
            workflow_execution_retention_period=retention,
            description=f"Apotheon SDLC namespace ({namespace})",
        )
        await service.register_namespace(req)
        logger.info(
            "Namespace '%s' created (retention: %d days)", namespace, retention_days
        )
        return "created"
    except Exception as exc:
        raise RuntimeError(f"Failed to create namespace '{namespace}': {exc}") from exc


async def main_async(host: str, namespace: str, retention_days: int) -> int:
    import json
    try:
        status = await ensure_namespace(host, namespace, retention_days)
        print(json.dumps({"status": "ok", "namespace": namespace, "result": status}, indent=2))
        return 0
    except Exception as exc:
        logger.error("init_temporal_namespace failed: %s", exc)
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Apotheon Temporal namespace")
    parser.add_argument("--host", default=TEMPORAL_HOST)
    parser.add_argument("--namespace", default=TEMPORAL_NAMESPACE)
    parser.add_argument("--retention", type=int, default=RETENTION_DAYS, dest="retention_days")
    args = parser.parse_args()

    return asyncio.run(main_async(args.host, args.namespace, args.retention_days))


if __name__ == "__main__":
    sys.exit(main())