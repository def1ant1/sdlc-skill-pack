#!/usr/bin/env bash
set -euo pipefail

for cmd in docker python3 curl; do
  command -v "$cmd" >/dev/null || { echo "missing dependency: $cmd"; exit 1; }
done

docker compose version >/dev/null

echo "[ok] docker, compose, python, and curl available"
docker compose ps
