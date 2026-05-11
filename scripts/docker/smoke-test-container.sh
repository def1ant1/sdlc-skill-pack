#!/usr/bin/env bash
set -euo pipefail

docker compose exec -T runtime python scripts/validation/validate_skill_structure.py .
docker compose exec -T runtime python scripts/validation/validate_frontmatter.py .
docker compose exec -T runtime python scripts/runtime/execute_workflow.py --dry-run --plan workflows/fixtures/oldfarmtrucks/launch-readiness.yaml || true
curl -fsS http://localhost:8000/health

echo "smoke tests completed"
