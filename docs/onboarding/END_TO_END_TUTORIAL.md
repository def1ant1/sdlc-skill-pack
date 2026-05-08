# End-to-End Tutorial: Plan, Execute, and Analyze a Workflow

This tutorial walks through a complete Apotheon run — from stating an objective to
reviewing memory observations and telemetry — using only the local execution engine
(no Temporal required).

---

## Prerequisites

| Requirement | Check |
|---|---|
| Python 3.11+ | `python --version` |
| `ANTHROPIC_API_KEY` set | `echo $ANTHROPIC_API_KEY` |
| Repo dependencies installed | `pip install -e ".[dev]"` |
| (Optional) Qdrant running | `docker compose up -d qdrant` |
| (Optional) Ollama running | `docker compose up -d ollama` |

Memory persistence (Qdrant + Ollama) is optional. If unavailable, the workflow still
runs — observations are simply not stored for later retrieval.

---

## Step 1 — Validate the skill repository

Before running anything, confirm the skill structure is valid:

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
```

Both commands should exit 0. If not, see `docs/onboarding/SKILL_AUTHORING_GUIDE.md`.

---

## Step 2 — Plan a workflow

Pass a plain-English objective to the SDLC planner:

```bash
python scripts/orchestration/plan_workflow.py "Build a payment service with Stripe integration"
```

The planner emits a JSON plan to stdout:

```json
{
  "plan_id": "WF-20260508-a1b2c3d4",
  "objective": "Build a payment service with Stripe integration",
  "phases_detected": ["backend", "devsecops", "qa", "release"],
  "skill_chain": [
    {"step": 1, "skill": "requirements-analysis", "phase": "requirements"},
    {"step": 2, "skill": "backend-engineering",   "phase": "backend"},
    {"step": 3, "skill": "devsecops",             "phase": "devsecops"},
    {"step": 4, "skill": "qa",                    "phase": "qa"},
    {"step": 5, "skill": "release-management",    "phase": "release"}
  ]
}
```

Save the plan:

```bash
python scripts/orchestration/plan_workflow.py \
  "Build a payment service with Stripe integration" \
  > payment_plan.json
```

### GTM variant

For a go-to-market objective, use the GTM planner instead:

```bash
python scripts/orchestration/plan_gtm_workflow.py \
  "Launch payment service to enterprise market" \
  > gtm_plan.json
```

---

## Step 3 — Dry-run the plan

Before spending API tokens, verify the plan looks correct:

```bash
python scripts/runtime/execute_workflow.py \
  --plan payment_plan.json \
  --dry-run
```

Expected output:

```json
{
  "run_id": "RUN-1746729600-abc12345",
  "status": "dry_run",
  "total_steps": 5,
  "steps": [
    {"step": 1, "skill": "requirements-analysis", "status": "dry_run"},
    {"step": 2, "skill": "backend-engineering",   "status": "dry_run"},
    ...
  ]
}
```

All steps show `"status": "dry_run"` — no Claude calls were made.

---

## Step 4 — Execute the workflow

Run the plan for real (requires `ANTHROPIC_API_KEY`):

```bash
python scripts/runtime/execute_workflow.py \
  --plan payment_plan.json \
  > execution_log.json
```

You can also pipe the planner directly into the executor:

```bash
python scripts/orchestration/plan_workflow.py \
  "Build a payment service with Stripe integration" | \
  python scripts/runtime/execute_workflow.py \
  > execution_log.json
```

### What happens during execution

For each step, the executor:

1. **Loads context** — `ContextManager.load()` checks Qdrant for a prior snapshot
   (enables resumption after HITL pauses or crashes)
2. **Fetches memory** — `ContextManager.retrieve_relevant()` finds semantically
   similar observations from past runs and injects them into the skill prompt
3. **Calls the skill** — `skill_activity.run_skill_activity()` loads the skill's
   `SKILL.md`, builds the prompt, calls Claude, detects HITL gates
4. **Persists results** — `ContextManager.save_step()` embeds the output and upserts
   to Qdrant; `ContextManager.save_context()` snapshots the full context packet
5. **Emits telemetry** — duration, gate result, and artifact counts are recorded
   to `telemetry.log.yaml`

### HITL gates

If a step requires human approval (e.g. `devsecops`, `release-management`), execution
pauses:

```json
{
  "status": "paused_for_hitl",
  "paused_at_step": 3,
  "steps": [...]
}
```

Approve and resume:

```bash
apotheon approve <run-id>
# or via CLI directly:
python scripts/runtime/hitl_handler.py approve <run-id>
```

---

## Step 5 — Review the execution log

```bash
python -m json.tool execution_log.json
```

Key fields:

| Field | Description |
|---|---|
| `run_id` | Unique run identifier (e.g. `RUN-1746729600-abc12345`) |
| `status` | `completed`, `failed`, `paused_for_hitl`, or `dry_run` |
| `total_steps` | Number of skills in the chain |
| `steps[].duration_ms` | Time spent on each skill |
| `steps[].output` | First 500 chars of the skill's output |
| `steps[].hitl_required` | Whether this step triggered a HITL gate |

---

## Step 6 — Inspect the operator console

```bash
# One-shot status table (requires rich: pip install rich)
python scripts/ui/operator_console.py

# Auto-refresh every 5 seconds
python scripts/ui/operator_console.py --live

# Show only HITL queue
python scripts/ui/operator_console.py --hitl

# Plain text (no rich dependency)
python scripts/ui/operator_console.py --plain
```

The console shows:
- **Workflow History** — recent run IDs, statuses, step progress
- **HITL Approval Queue** — runs blocked on human approval
- **Connector Health** — status of Salesforce, Jira, Slack, etc.
- **Memory Layer** — Qdrant reachability and collection counts

---

## Step 7 — Search memory for prior observations

After a workflow completes, its step outputs live in the `apotheon-observations`
Qdrant collection. Retrieve them semantically:

```bash
python scripts/memory/retrieve_context.py \
  "Stripe payment service architecture decisions" \
  --top-k 5 \
  --min-score 0.65
```

Response:

```json
{
  "query": "Stripe payment service architecture decisions",
  "result_count": 3,
  "results": [
    {
      "score": 0.8412,
      "obs_id": "RUN-1746729600-abc12345-step-2",
      "content": "backend-engineering output...",
      "obs_type": "step_output",
      "observed_at": "2026-05-08T14:32:10Z"
    }
  ]
}
```

---

## Step 8 — Review telemetry

Each step writes a record to `telemetry.log.yaml`:

```bash
cat telemetry.log.yaml
```

Sample record:

```yaml
event_id: TEL-20260508-042
timestamp: "2026-05-08T14:32:11Z"
workflow_id: RUN-1746729600-abc12345
phase: backend-engineering
gate_result: PASS
tokens_used: 0
duration_ms: 3412
artifacts_produced:
  - backend-engineering_output
```

Anomaly alerts fire when metrics cross thresholds defined in
`scripts/telemetry/record_telemetry_event.py` (e.g. quality_score < 40).

---

## Step 9 — Check skill gaps

Detect any skill dependencies that are declared but missing on disk:

```bash
python scripts/orchestration/detect_skill_gaps.py
```

Gaps are reported as:

```
Missing skills (not in skills/ or core/):
  custom-billing-validator
    declared by: payment-orchestration

Missing dependencies (declared but not registered):
  (none)
```

Use `create_skill.py` to scaffold any missing skill:

```bash
python scripts/generators/create_skill.py custom-billing-validator
```

---

## Common patterns

### Chaining planner output directly

```bash
python scripts/orchestration/plan_workflow.py "Refactor auth service to OAuth2" | \
  python scripts/runtime/execute_workflow.py --mode local
```

### Saving plan for later

```bash
python scripts/orchestration/plan_workflow.py "Deploy ML model to production" > plan.json
# ... review the plan ...
python scripts/runtime/execute_workflow.py --plan plan.json
```

### Running in Temporal mode

Start the worker in one terminal:

```bash
python scripts/runtime/temporal_worker.py
```

Submit the plan from another:

```bash
EXECUTION_MODE=temporal \
  python scripts/runtime/execute_workflow.py --plan plan.json --mode temporal
```

The workflow becomes durable and survives worker restarts. Monitor at
`http://localhost:8080` (Temporal UI).

### Using the CLI

All of the above is available through the `apotheon` CLI:

```bash
apotheon run "Build a payment service with Stripe integration"
apotheon dry-run "Build a payment service with Stripe integration"
apotheon status
apotheon approve <run-id>
apotheon skill list
apotheon skill gaps
apotheon memory search "Stripe architecture"
apotheon connector health
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ANTHROPIC_API_KEY not set` | Missing env var | `export ANTHROPIC_API_KEY=sk-ant-...` |
| `SKILL.md not found` | Skill name typo | Run `apotheon skill list` to verify names |
| Qdrant connection refused | Qdrant not running | `docker compose up -d qdrant` |
| Embedding unavailable | Ollama not running | `docker compose up -d ollama` (or set `EMBEDDING_BACKEND=openai`) |
| `temporalio not installed` | Missing dep | `pip install 'apotheon[temporal]'` |
| Workflow stuck at HITL | Pending approval | `apotheon approve <run-id>` |