#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
docker compose up -d --build
scripts/docker/wait-for-services.sh
python scripts/memory/init_collections.py || true
python scripts/runtime/init_temporal_namespace.py || true

echo "local stack initialized"
