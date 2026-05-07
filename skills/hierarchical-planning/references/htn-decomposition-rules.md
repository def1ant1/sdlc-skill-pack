# HTN Decomposition Rules Reference

## HTN Core Concepts

### Task Types

| Type | Description | Example |
|---|---|---|
| Primitive task | Directly executable action; no further decomposition | `execute_sql_query(query)` |
| Compound task | Requires decomposition via method; not directly executable | `deploy_service(service)` |
| Goal task | Achieved state rather than action; decomposed to achieve it | `achieve(test_coverage ≥ 0.80)` |

### Method Definition Format

```yaml
method:
  name: "deploy-service-standard"
  applies_to: "compound_task:deploy_service"

  preconditions:
    - "service.build_status == SUCCESS"
    - "environment.capacity_available >= service.resource_requirements"
    - "deployment.approval_status IN [APPROVED, AUTO_APPROVED]"

  subtask_network:
    - id: t1
      task: "run_smoke_tests(service)"
      type: primitive
    - id: t2
      task: "create_deployment_checkpoint(service)"
      type: primitive
      depends_on: [t1]
    - id: t3
      task: "scale_down_old_version(service)"
      type: primitive
      depends_on: [t2]
    - id: t4
      task: "deploy_new_version(service)"
      type: primitive
      depends_on: [t3]
    - id: t5
      task: "run_health_checks(service)"
      type: primitive
      depends_on: [t4]
    - id: t6
      task: "verify_traffic_routing(service)"
      type: primitive
      depends_on: [t5]

  postconditions:
    - "service.version == target_version"
    - "service.health_status == HEALTHY"

  failure_handling:
    on_t4_failure: "invoke_task(rollback_deployment(service))"
    on_t5_failure: "invoke_task(rollback_deployment(service))"
```

---

## Decomposition Algorithm

```
FUNCTION htn_plan(task_network, state, depth=0):
    IF depth > MAX_DEPTH:
        RETURN FAILURE("Max decomposition depth exceeded")

    IF all tasks in task_network are primitive:
        # Check all primitives are applicable in current state
        FOR each primitive_task t IN task_network:
            IF NOT applicable(t, state):
                RETURN FAILURE(f"Primitive {t} not applicable in state")
            state = apply(t, state)
        RETURN task_network  # This is the plan

    # Find first compound task
    compound = first_compound_task(task_network)

    # Find applicable methods for this compound task
    applicable_methods = [m FOR m IN methods[compound.type]
                          IF satisfies(m.preconditions, state)]

    IF NOT applicable_methods:
        RETURN FAILURE(f"No applicable method for {compound}")

    # Try each method (depth-first with backtracking)
    FOR each method m IN applicable_methods:
        subtask_network = instantiate(m.subtask_network, compound.args)
        new_network = replace(task_network, compound, subtask_network)
        result = htn_plan(new_network, state, depth + 1)
        IF result != FAILURE:
            RETURN result

    RETURN FAILURE("All methods exhausted for " + compound)
```

---

## Method Selection Heuristics

When multiple methods apply, rank by:

```
method_score = (
    precondition_match_strength × 0.40 +  # How closely preconditions match
    historical_success_rate × 0.30 +       # Past success rate in similar states
    estimated_cost_efficiency × 0.20 +     # Cost/duration of generated subtasks
    postcondition_coverage × 0.10          # How well postconditions satisfy parent task needs
)
```

**Special ordering rules:**
1. If current state is in DEGRADED mode, prefer RESILIENT method variants
2. If latency budget is tight (< 20% headroom), prefer FAST method variants
3. If a rollback method exists, prefer methods with explicit rollback subtasks for HIGH risk tasks

---

## Standard Decomposition Patterns

### Pattern 1: Sequential Pipeline

```
task: process_data_pipeline
method: sequential-stages
subtasks: [ingest → validate → transform → load → verify]
constraint: each stage must complete before next starts
```

### Pattern 2: Parallel Workstreams

```
task: build_full_system
method: parallel-components
subtasks: [build_frontend ∥ build_backend ∥ build_database]
sync_point: after all parallel tasks → integration_test
```

### Pattern 3: Iterative Refinement

```
task: achieve_quality_threshold
method: iterative-improvement
subtasks:
  LOOP WHILE metric < threshold AND iteration < max_iterations:
    measure_quality → identify_gaps → apply_improvements
```

### Pattern 4: Conditional Branch

```
task: handle_authentication
method: conditional-auth
subtasks:
  IF user.mfa_enabled:
    verify_password → verify_mfa_token → grant_access
  ELSE:
    verify_password → request_mfa_enrollment → grant_access
```

---

## Domain Decomposition Library

### SDLC Domain Methods

```yaml
compound_tasks:
  - name: "develop_feature"
    methods: [agile-sprint, waterfall-phase, kanban-flow]

  - name: "release_service"
    methods: [blue-green-deploy, canary-deploy, rolling-deploy, hotfix-deploy]

  - name: "resolve_incident"
    methods: [triage-contain-resolve, escalate-to-on-call, automated-remediation]

  - name: "onboard_engineer"
    methods: [standard-30-60-90, accelerated-2-week, contractor-limited-access]
```

---

## Plan Quality Metrics

```
plan_quality = (
    completeness_score ×  0.35 +   # All goal states achievable
    efficiency_score × 0.25 +       # Minimal redundant steps
    robustness_score × 0.25 +       # Has recovery paths for failure modes
    feasibility_score × 0.15        # Preconditions satisfiable in current state
)

completeness_score = 1.0 if postconditions_of_plan ⊇ goal_conditions else 0.0
efficiency_score = optimal_plan_length / actual_plan_length
robustness_score = tasks_with_recovery_path / total_tasks
feasibility_score = initial_preconditions_satisfied / total_initial_preconditions
```