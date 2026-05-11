# Local Laptop Setup Runbook

**Purpose:** Get Apotheon AI Company OS fully configured and testable on a local laptop before enabling external side effects, schedules, or Temporal promotion.

This runbook assumes the repo is already cloned and Python is available locally.

---

## 1. Local Setup Objectives

A complete laptop setup means you can:

1. Install dependencies.
2. Start local infrastructure services.
3. Initialize memory and workflow infrastructure.
4. Run validation gates.
5. Generate skill inventory and dependency reports.
6. Plan workflows from objectives.
7. Dry-run workflows without LLM/API side effects.
8. Execute controlled local workflows.
9. Preview and run local schedules once schedule tooling exists.
10. Generate local operational reports.

---

## 2. Recommended Local Directory Policy

Generated runtime files should stay out of git unless explicitly promoted.

Expected local-only paths:

```text
runtime/
  workflow_runs/
  schedule_runs/
  artifacts/
  reports/
workflows/generated/
schedules/local/
dist/
.env
```

Recommended `.gitignore` additions if missing:

```gitignore
.env
.env.*
!.env.example
runtime/workflow_runs/*
runtime/schedule_runs/*
runtime/artifacts/*
runtime/reports/*
workflows/generated/*
schedules/local/*
dist/*.zip
dist/*.sha256
dist/*.manifest.json
```

---

## 3. Environment File

Create `.env` locally:

```bash
cat > .env <<'EOF'
EXECUTION_MODE=local
LOG_LEVEL=INFO
QDRANT_URL=http://localhost:6333
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=apotheon-dev
TEMPORAL_TASK_QUEUE=apotheon-sdlc
EMBEDDING_BACKEND=ollama
OLLAMA_URL=http://localhost:11434
EMBEDDING_DIMS=768
CLAUDE_MODEL=claude-sonnet-4-6
MAX_TOKENS=4096
EOF
```

Only add API keys when you are ready for live execution:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=... # only if EMBEDDING_BACKEND=openai
```

For dry-run testing, API keys should not be required.

---

## 4. Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Validation:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

---

## 5. Start Local Infrastructure

If `docker-compose.yml` exists:

```bash
docker compose up -d qdrant temporal temporal-ui
```

If it does not exist, create one based on `docs/onboarding/DEPLOYMENT.md`, then run the same command.

Check services:

```bash
docker compose ps
curl http://localhost:6333/collections || true
```

Expected:

- Qdrant on `http://localhost:6333`
- Temporal on `localhost:7233`
- Temporal UI on `http://localhost:8080`

---

## 6. Initialize Local Memory and Temporal

```bash
python scripts/memory/init_collections.py
python scripts/runtime/init_temporal_namespace.py
```

If Temporal is not needed yet, you can skip namespace initialization and stay in `EXECUTION_MODE=local`.

---

## 7. Run Baseline Validation

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
pytest --tb=short -q
```

Then run V9/release gates:

```bash
python scripts/run_premerge_checks.py
```

If this is slow, run individual gates while developing:

```bash
python scripts/validate_backlog_truth.py
python scripts/validate_skill_contracts.py
python scripts/check_context_budget.py
python scripts/generate_skill_inventory.py
python scripts/generate_dependency_graph.py
python scripts/detect_skill_overlap.py
python scripts/validate_skill_evals.py
python scripts/validate_telemetry_events.py
```

---

## 8. Generate Reports

```bash
python scripts/generate_release_reports.py
```

Expected outputs include reports such as:

```text
reports/repo_truth_report.md
reports/skill_inventory.md
reports/skill_dependency_graph.json
reports/orchestration_map.md
reports/routing_collision_report.md
```

If generated reports change, commit them intentionally or regenerate after implementation changes.

---

## 9. Test Existing Workflow Planning

SDLC workflow:

```bash
python scripts/orchestration/plan_workflow.py "Build a secure REST API" > workflows/generated/test-sdlc-plan.json
python scripts/runtime/execute_workflow.py --plan workflows/generated/test-sdlc-plan.json --dry-run
```

GTM workflow:

```bash
python scripts/orchestration/plan_gtm_workflow.py "Launch OldFarmTrucks.com as a classic truck dealership" > workflows/generated/test-gtm-plan.json
python scripts/runtime/execute_workflow.py --plan workflows/generated/test-gtm-plan.json --dry-run
```

Expected behavior:

- Plan JSON is generated.
- Dry run validates step order.
- Dry run does not call external LLMs or connectors.
- Any missing skills or schema problems are reported clearly.

---

## 10. Business Workflow Setup Target

The next local milestone is to implement and test:

```text
scripts/orchestration/plan_business_workflow.py
scripts/orchestration/plan_customer_workflow.py
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_inventory_workflow.py
```

Initial test objectives:

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Launch OldFarmTrucks.com as a classic truck dealership in 30 days" \
  --dry-run --json --output workflows/generated/oldfarmtrucks-launch.json

python scripts/orchestration/plan_customer_workflow.py \
  "Build lifecycle marketing automation for OldFarmTrucks.com" \
  --dry-run --json --output workflows/generated/oldfarmtrucks-lifecycle.json

python scripts/orchestration/plan_inventory_workflow.py \
  "Find classic farm truck acquisition opportunities within 300 miles" \
  --dry-run --json --output workflows/generated/oldfarmtrucks-market-scan.json
```

Each output should validate against the workflow plan schema once implemented.

---

## 11. Schedule Setup Target

The next scheduling milestone is to implement:

```text
scripts/schedules/validate_schedule.py
scripts/schedules/preview_schedule.py
scripts/schedules/run_due_schedules.py
schemas/workflow-schedule.schema.json
schedules/examples/
```

Target local schedules:

```text
schedules/examples/oldfarmtrucks-daily-market-scan.yaml
schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
schedules/examples/oldfarmtrucks-weekly-customer-lifecycle.yaml
schedules/examples/oldfarmtrucks-monthly-pricing-model-review.yaml
schedules/examples/oldfarmtrucks-quarterly-strategy-review.yaml
```

After implementation:

```bash
python scripts/schedules/validate_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
python scripts/schedules/preview_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml --count 5
python scripts/schedules/run_due_schedules.py --dry-run
```

---

## 12. Live Execution Guardrails

Do not enable real side effects until all are true:

```text
[ ] Dry-run execution is stable
[ ] External connector credentials are configured intentionally
[ ] Customer communication policy is linked
[ ] Data scraping policy is linked
[ ] Financial controls are linked
[ ] HITL approval gates are enforced
[ ] Run history is stored
[ ] Schedule history is stored
[ ] Local ops report is generated
```

Live execution should initially be limited to read-only operations.

---

## 13. Recommended Local Development Order

1. Confirm validation and tests pass.
2. Generate reports.
3. Run SDLC dry-run.
4. Run GTM dry-run.
5. Implement workflow plan schema/validator.
6. Implement business/customer/finance/inventory planners.
7. Add OldFarmTrucks executable workflow fixtures.
8. Implement schedule schema and preview.
9. Implement due-schedule dry-run runner.
10. Add local run history.
11. Add local ops report.
12. Only then enable controlled live execution.

---

## 14. Troubleshooting

For structured remediation, see:

- `docs/onboarding/TROUBLESHOOTING.md`
- `docs/onboarding/OPERATOR_RUNBOOK.md`

Recommended local recovery command bundle:

```bash
apotheon doctor
apotheon diagnostics
apotheon connectors check
apotheon local-apps check --compose-file docker-compose.yml
```

### Qdrant not reachable

```bash
docker compose ps
curl http://localhost:6333/collections
```

### Temporal not reachable

```bash
docker compose ps
open http://localhost:8080
```

### Dry run attempts external call

This is a blocker. Add or fix tests under:

```text
tests/runtime/test_dry_run_no_external_calls.py
```

### Planner emits missing skills

Run:

```bash
python scripts/generate_skill_inventory.py --root .
python scripts/orchestration/detect_skill_gaps.py .
```

Then either update planner routing or create missing skill stubs.

### Reports change unexpectedly

Run:

```bash
python scripts/generate_release_reports.py
git diff -- reports/
```

Commit regenerated reports only after confirming the changes are intentional.

---

## 15. Definition of Fully Configured Local Laptop

Your laptop setup is complete when:

```text
[ ] Python env is installed
[ ] Docker services are running
[ ] Qdrant collections are initialized
[ ] Temporal namespace is initialized or local-only mode is chosen
[ ] Baseline validation passes
[ ] Premerge checks pass
[ ] Reports generate cleanly
[ ] SDLC dry-run works
[ ] GTM dry-run works
[ ] Business planner dry-run works
[ ] Customer planner dry-run works
[ ] Inventory planner dry-run works
[ ] Example schedules validate
[ ] Schedule preview works
[ ] Due schedule dry-run works
[ ] Local run history is written
[ ] Local ops report is generated
[ ] No dry-run path calls external APIs
```


### Scheduling update (MB-P0-010)
Scheduling tooling is implemented under `scripts/schedules/` with schema + runtime run recording in `runtime/schedule_runs/`. Use `python scripts/schedules/run_due_schedules.py --dry-run` for safe due-window checks.
