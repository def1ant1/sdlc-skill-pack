#!/usr/bin/env bash
set -euo pipefail

services=(postgres redis qdrant temporal runtime)
for svc in "${services[@]}"; do
  echo "waiting for $svc health..."
  for _ in {1..60}; do
    status=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "apotheon-$svc" 2>/dev/null || true)
    [[ "$status" == "healthy" || "$status" == "none" ]] && break
    sleep 2
  done
  echo "$svc status: ${status:-unknown}"
  [[ "${status:-unknown}" == "healthy" || "${status:-unknown}" == "none" ]] || exit 1
done
