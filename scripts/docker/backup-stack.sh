#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-dist/backups/docker}"
mkdir -p "$OUTPUT_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROJECT="${COMPOSE_PROJECT_NAME:-apotheon}"
ARCHIVE="$OUTPUT_DIR/docker-stack-backup-${STAMP}.tar.gz"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

docker compose config > "$TMP_DIR/compose.rendered.yaml"
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}' > "$TMP_DIR/images.txt"
docker volume ls --format '{{.Name}}' | rg "^${PROJECT}" > "$TMP_DIR/volumes.txt" || true

tar -czf "$ARCHIVE" -C "$TMP_DIR" .
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
echo "archive=$ARCHIVE"
echo "checksum=$ARCHIVE.sha256"
