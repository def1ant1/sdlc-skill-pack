#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="${1:-}"
MODE="${2:---dry-run}"
if [[ -z "$ARCHIVE" ]]; then
  echo "usage: $0 <archive.tar.gz> [--dry-run|--live]"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

tar -xzf "$ARCHIVE" -C "$TMP_DIR"

echo "Restore preview from $ARCHIVE"
for file in compose.rendered.yaml images.txt volumes.txt; do
  if [[ -f "$TMP_DIR/$file" ]]; then
    echo "PLAN load $file"
  fi
done

if [[ "$MODE" == "--dry-run" ]]; then
  echo "mode=dry-run"
  exit 0
fi

if [[ "$MODE" != "--live" ]]; then
  echo "unknown mode: $MODE"
  exit 1
fi

if [[ -f "$ARCHIVE.sha256" ]]; then
  sha256sum -c "$ARCHIVE.sha256"
fi

echo "Applying compose restore from rendered config"
docker compose -f "$TMP_DIR/compose.rendered.yaml" up -d

echo "restore complete"
