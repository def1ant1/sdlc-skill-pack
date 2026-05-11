# Runtime Components

Apotheon's runtime stack translates a skill execution plan into durable,
observable, and recoverable LLM-powered workflow steps.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI / API Layer                          │
│  plan_workflow.py   plan_gtm_workflow.py   execute_workflow.py  │
└────────────────────────────┬────────────────────────────────────┘
                             │ workflow plan JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Execution Engine                            │
│                                                                 │
│   LOCAL MODE                    TEMPORAL MODE                   │
│   execute_local()               temporal_worker.py              │
│   (sequential, in-process)      ApotheonWorkflow                │
│                                 (durable, retryable)            │
└────────────────────────────┬────────────────────────────────────┘
                             │ SkillActivityInput
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Skill Activity Layer                        │
│                    skill_activity.py                            │
│                                                                 │
│  1. load_skill_contract()  → SKILL.md system prompt            │
│  2. build user message     → objective + context packet         │
│  3. call_claude()          → Anthropic Messages API             │
│  4. HITL detection         → phrase scan on output              │
│  5. return SkillActivityOutput                                  │
└──────────────┬──────────────────────────┬───────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────────────────┐
│   Anthropic API      │    │         Memory Layer                │
│   claude-sonnet-4-6  │    │                                     │
│   (or configured     │    │  embed_observation.py               │
│    CLAUDE_MODEL)     │    │  retrieve_context.py                │
└──────────────────────┘    │  init_collections.py                │
                            │          │                          │
                            │          ▼                          │
                            │    ┌──────────┐                     │
                            │    │  Qdrant  │ (vector DB)         │
                            │    └──────────┘                     │
                            └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Connector Layer                             │
│                                                                 │
│  base_connector.py          auth/                               │
│  ├─ BaseConnector            ├─ oauth2_client.py                │
│  ├─ RateLimiter              ├─ api_key_client.py               │
│  └─ resolve_secret()         └─ mtls_client.py                  │
│                                                                 │
│  salesforce_connector.py    ga4_connector.py                    │
│  servicenow_connector.py    slack_connector.py                  │
│  jira_connector.py          health_check.py                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Plan generation

```
User objective (string)
    → plan_workflow.py / plan_gtm_workflow.py
    → skill_chain (ordered list of skill names + metadata)
    → workflow_plan.json
```

### 2. Local execution

```
workflow_plan.json
    → execute_local()
    → for each step:
        build SkillActivityInput (skill_name, objective, context_packet)
        → run_skill_activity()
            → load SKILL.md → system prompt
            → call Claude API
            → detect HITL gate phrases
            → return SkillActivityOutput
        → if success: append to prior_outputs, update context_packet
        → if HITL: pause, record paused_at_step
        → if failure: record error, break
    → return execution_log (JSON)
```

### 3. Temporal execution

```
workflow_plan.json
    → ApotheonWorkflow.run(plan)
    → for each step:
        workflow.execute_activity("run_skill", inp_dict,
            start_to_close_timeout=10min, retry_policy=3x)
        → run_skill_temporal() [Temporal activity]
            → run_skill_activity() (same as local)
        → on HITL: workflow waits for hitl_approved signal
        → on failure after retries: workflow fails with error
    → return execution_log
```

---

## Key Design Decisions

### No third-party HTTP libraries
All HTTP calls use Python stdlib `urllib.request`. This avoids pip dependency
conflicts in restricted environments and keeps the connector layer portable.

### Deterministic observation UUIDs
`embed_observation.py` uses `uuid.uuid5(NAMESPACE_URL, obs_id)` to make
Qdrant upserts idempotent — re-embedding the same observation overwrites
rather than duplicates.

### HITL as phrase detection (current)
`skill_activity.py` detects HITL gates by scanning output text for approval
phrases. This is intentionally simple. The roadmap (V9-P100) upgrades this
to structured `hitl_gates` frontmatter declarations with Temporal signal
integration.

### Context packet accumulation
The context packet grows across steps: each completed skill appends its name
to `artifacts` and its last 2000 chars of output are passed as
`additional_context` to the next skill. This gives downstream skills
awareness of upstream decisions without requiring shared state.

---

## Configuration Reference

See `docs/onboarding/DEPLOYMENT.md` for the full environment variable
reference and deployment procedures.
## Dry-Run Contract and Guarantees

`execute_workflow.py --dry-run` now enforces a global dry-run execution contract:

- **No outbound connector side-effects:** runtime sets `APOTHEON_DRY_RUN=1` and `BaseConnector._request()` hard-fails with `DryRunSideEffectBlocked` before any external HTTP call.
- **Per-step side-effect tags:** each step includes `side_effect_classification` as one of:
  - `read-only`
  - `simulated-mutation`
  - `real-mutation`
  During dry-run, mutating steps are surfaced as `simulated-mutation`.
- **Deterministic artifacts:** dry-run emits reproducible metadata, including a deterministic run id (`DRYRUN-<plan-hash>`), fixed timestamps (`1970-01-01T00:00:00Z`), sorted step output in CLI JSON, and stable key ordering.
- **Governance behavior preserved:** workflow governance semantics (including high-risk step tagging and HITL-relevant classification context) remain visible in dry-run logs even when execution is non-invasive.


## Runtime Hardening (MB-P0-007)
- Live mode now enforces controlled provider selection via `APOTHEON_PROVIDER` allow-list (`anthropic`, `local`).
- Dry-run forces `local-stub` model fallback and never calls external inference APIs.
- Skill outputs must parse as structured JSON and include required fields (`status`, `summary`).
- Run records now persist estimated cost and correlation IDs per step for operator traceability.
