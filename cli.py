#!/usr/bin/env python3
"""
apotheon — Unified CLI for the Apotheon AI Company OS.

Usage:
    apotheon run "<objective>"              Plan + execute an SDLC workflow
    apotheon gtm "<objective>"             Plan + execute a GTM workflow
    apotheon dry-run "<objective>"         Plan without executing (SDLC)
    apotheon gtm-dry-run "<objective>"     Plan without executing (GTM)
    apotheon status                        Show active workflows and HITL queue
    apotheon approve <run-id>              Approve a pending HITL gate
    apotheon reject <run-id>               Reject a pending HITL gate
    apotheon logs <run-id>                 Show step-by-step output for a run
    apotheon skill list                    List all registered skills
    apotheon skill gaps                    Show unresolved skill dependencies
    apotheon connector health              Check connector availability
    apotheon memory search "<query>"       Semantic search across Qdrant
    apotheon memory init                   Initialize Qdrant collections
    apotheon validate                      Run all validation checks
    apotheon bootstrap                     Full OS health check
    apotheon init                          First-time setup: DB, Qdrant, env check
    apotheon doctor                        Diagnose environment health + fixes
    apotheon diagnostics                   Generate runtime diagnostics artifacts
    apotheon workflows resume <run_id>     Resume/recover a workflow from history
    apotheon schedules repair              Repair schedule state + run due jobs
    apotheon connectors check              Run connector readiness checks
    apotheon local-apps check              Verify local compose app health
    apotheon backup create                 Create local backup archive
    apotheon backup restore --dry-run ...  Preview backup restore actions

Install:
    pip install -e .                       Installs 'apotheon' into PATH

Environment:
    ANTHROPIC_API_KEY    Required for workflow execution
    EXECUTION_MODE       local | temporal (default: local)
    QDRANT_URL           Vector store URL (default: http://localhost:6333)
    TEMPORAL_HOST        Temporal gRPC address (default: localhost:7233)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.scheduling.task_scheduler_runtime import set_schedule_state

REPO_ROOT = Path(__file__).parent
SCRIPTS = REPO_ROOT / "scripts"

# Ensure scripts subdirs are on path for imports
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _python() -> str:
    return sys.executable


def _run(cmd: list[str], input_text: str | None = None) -> int:
    """Run a command, streaming output to stdout/stderr. Returns exit code."""
    result = subprocess.run(cmd, input=input_text, text=True)
    return result.returncode


def _capture(cmd: list[str], input_text: str | None = None) -> tuple[int, str]:
    """Run a command and capture stdout. Returns (code, stdout)."""
    result = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    return result.returncode, result.stdout


def _script(rel_path: str) -> str:
    return str(REPO_ROOT / rel_path)


def _print_json(data: dict | list) -> None:
    print(json.dumps(data, indent=2))


def _err(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


def _parse_output_mode(args: list[str]) -> tuple[str, list[str]]:
    mode = "human"
    rest: list[str] = []
    i = 0
    while i < len(args):
        token = args[i]
        if token == "--json":
            mode = "json"
            i += 1
            continue
        if token == "--output":
            if i + 1 >= len(args):
                raise ValueError("--output requires a value: human|json")
            value = args[i + 1].lower()
            if value not in {"human", "json"}:
                raise ValueError("--output must be one of: human, json")
            mode = value
            i += 2
            continue
        rest.append(token)
        i += 1
    return mode, rest


def _print_mode(data: dict[str, Any], mode: str) -> None:
    if mode == "json":
        _print_json(data)
        return
    for line in data.get("lines", []):
        print(line)


def _list_run_files(history_dir: Path) -> list[Path]:
    if not history_dir.exists():
        return []
    return sorted(history_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def cmd_workflows(args: list[str]) -> int:
    if not args:
        return _err("usage: apotheon workflows <list|run|resume>")
    subcommand = args[0]
    rest = args[1:]
    if subcommand == "run":
        dry_run = "--execute" not in rest
        run_args = [a for a in rest if a != "--execute"]
        if dry_run:
            return cmd_dry_run(run_args)
        return cmd_run(run_args)
    if subcommand == "resume":
        if not rest:
            return _err("usage: apotheon workflows resume <run_id>")
        return _run([_python(), _script("scripts/runtime/recovery.py"), "--run-id", rest[0]])
    if subcommand == "list":
        try:
            mode, flags = _parse_output_mode(rest)
        except ValueError as exc:
            return _err(str(exc))
        limit = 20
        if "--limit" in flags:
            idx = flags.index("--limit")
            if idx + 1 >= len(flags):
                return _err("--limit requires an integer value")
            limit = int(flags[idx + 1])
        history_dir = Path("runtime/workflow_history")
        rows: list[dict[str, Any]] = []
        lines: list[str] = []
        for artifact in _list_run_files(history_dir)[:limit]:
            try:
                data = json.loads(artifact.read_text())
            except json.JSONDecodeError:
                continue
            row = {
                "run_id": data.get("run_id"),
                "status": data.get("status"),
                "objective": data.get("objective"),
                "started_at": data.get("started_at"),
                "completed_at": data.get("completed_at"),
            }
            rows.append(row)
            lines.append(f"{row['run_id']}  {row['status']}  {row['started_at']}  {row['objective']}")
        _print_mode({"runs": rows, "lines": lines}, mode)
        return 0
    return _err("usage: apotheon workflows <list|run|resume>")


def cmd_schedules(args: list[str]) -> int:
    if not args:
        return _err("usage: apotheon schedules <preview|run-due|repair|create|pause|archive>")
    subcommand = args[0]
    rest = args[1:]
    if subcommand == "preview":
        return _run([_python(), _script("scripts/scheduling/preview_schedule.py"), *rest])
    if subcommand == "run-due":
        return _run([_python(), _script("scripts/scheduling/run_due_schedules.py"), *rest])

    if subcommand == "pause":
        if not rest:
            return _err("usage: apotheon schedules pause <schedule_id>")
        return 0 if set_schedule_state(Path("schedules/registry.yaml"), rest[0], enabled=False) else 1
    if subcommand == "archive":
        if not rest:
            return _err("usage: apotheon schedules archive <schedule_id>")
        return 0 if set_schedule_state(Path("schedules/registry.yaml"), rest[0], enabled=False, archived=True) else 1
    if subcommand == "create":
        if len(rest) < 3:
            return _err("usage: apotheon schedules create <schedule_id> <mode:cron|interval|event> <target>")
        import yaml
        reg=Path("schedules/registry.yaml")
        payload=yaml.safe_load(reg.read_text()) or {"schedules": []}
        sid,mode,target=rest[0],rest[1],rest[2]
        sch={"schedule_id":sid,"mode":mode,"enabled":True,"owner":"chat","planner_target":target,"risk_tier":"medium","action":{"type":"workflow","target":target},"approval":{"required":True,"policy_ref":"shared/policies/ai-safety-policy.md"},"generate_task":True}
        if mode=="interval": sch["interval_minutes"]=60
        elif mode=="cron": sch["cron"]="0 * * * *"
        else: sch["event"]={"name":"manual"}
        payload.setdefault("schedules",[]).append(sch)
        reg.write_text(yaml.safe_dump(payload, sort_keys=False))
        print(f"created schedule {sid}")
        return 0

    if subcommand == "repair":
        print("Repairing schedule state...")
        locks_dir = Path("runtime/schedule_history/locks")
        removed = 0
        if locks_dir.exists():
            for lock_file in locks_dir.glob("*.lock.json"):
                lock_file.unlink(missing_ok=True)
                removed += 1
        print(f"Removed {removed} stale lock file(s).")
        return _run([_python(), _script("scripts/scheduling/run_due_schedules.py"), "--dry-run"])
    return _err("usage: apotheon schedules <preview|run-due|repair|create|pause|archive>")


def cmd_connectors(args: list[str]) -> int:
    if args and args[0] == "check":
        return _run([_python(), _script("scripts/connectors/health_check.py"), *args[1:]])
    return _err("usage: apotheon connectors check [--connector NAME|--json]")


def cmd_local_apps(args: list[str]) -> int:
    if not args or args[0] != "check":
        return _err("usage: apotheon local-apps check [--compose-file docker-compose.yml]")
    rest = args[1:]
    if "--compose-file" not in rest:
        rest = ["--compose-file", "docker-compose.yml", *rest]
    return _run([_python(), _script("scripts/local_apps/check_app_health.py"), *rest])


def cmd_backup(args: list[str]) -> int:
    if not args:
        return _err("usage: apotheon backup <create|restore>")
    if args[0] == "create":
        return _run([_python(), _script("scripts/backup/backup_local_state.py"), *args[1:]])
    if args[0] == "restore":
        return _run([_python(), _script("scripts/backup/restore_local_state.py"), *args[1:]])
    return _err("usage: apotheon backup <create|restore>")


def cmd_diagnostics(args: list[str]) -> int:
    return _run([_python(), _script("scripts/reports/generate_runtime_diagnostics.py"), *args])


def cmd_runs(args: list[str]) -> int:
    if not args or args[0] != "list":
        return _err("usage: apotheon runs list [--output human|json|--json]")
    try:
        mode, flags = _parse_output_mode(args[1:])
    except ValueError as exc:
        return _err(str(exc))
    limit = 20
    if "--limit" in flags:
        idx = flags.index("--limit")
        if idx + 1 >= len(flags):
            return _err("--limit requires an integer value")
        limit = int(flags[idx + 1])
    history_dir = Path("runtime/schedule_history")
    rows: list[dict[str, Any]] = []
    lines: list[str] = []
    if history_dir.exists():
        artifacts = sorted(history_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for artifact in artifacts[:limit]:
            try:
                data = json.loads(artifact.read_text())
            except json.JSONDecodeError:
                continue
            row = {
                "run_id": data.get("run_id"),
                "schedule_id": data.get("schedule_id"),
                "status": data.get("status"),
                "run_at": data.get("run_at"),
                "executed_at": data.get("executed_at"),
            }
            rows.append(row)
            lines.append(f"{row['run_id']}  {row['schedule_id']}  {row['status']}  {row['run_at']}")
    _print_mode({"runs": rows, "lines": lines}, mode)
    return 0


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_run(args: list[str]) -> int:
    """Plan and execute an SDLC workflow."""
    if not args:
        return _err("usage: apotheon run \"<objective>\"")
    objective = " ".join(args)
    code, plan_json = _capture([_python(), _script("scripts/orchestration/plan_workflow.py"), objective])
    if code != 0:
        return _err("planning failed")
    return _run(
        [_python(), _script("scripts/runtime/execute_workflow.py")],
        input_text=plan_json,
    )


def cmd_gtm(args: list[str]) -> int:
    """Plan and execute a GTM workflow."""
    if not args:
        return _err("usage: apotheon gtm \"<objective>\"")
    objective = " ".join(args)
    code, plan_json = _capture([_python(), _script("scripts/orchestration/plan_gtm_workflow.py"), objective])
    if code != 0:
        return _err("GTM planning failed")
    return _run(
        [_python(), _script("scripts/runtime/execute_workflow.py")],
        input_text=plan_json,
    )


def cmd_dry_run(args: list[str]) -> int:
    """Plan an SDLC workflow without executing."""
    if not args:
        return _err("usage: apotheon dry-run \"<objective>\"")
    objective = " ".join(args)
    code, plan_json = _capture([_python(), _script("scripts/orchestration/plan_workflow.py"), objective])
    if code != 0:
        return _err("planning failed")
    return _run(
        [_python(), _script("scripts/runtime/execute_workflow.py"), "--dry-run"],
        input_text=plan_json,
    )


def cmd_gtm_dry_run(args: list[str]) -> int:
    """Plan a GTM workflow without executing."""
    if not args:
        return _err("usage: apotheon gtm-dry-run \"<objective>\"")
    objective = " ".join(args)
    code, plan_json = _capture([_python(), _script("scripts/orchestration/plan_gtm_workflow.py"), objective])
    if code != 0:
        return _err("GTM planning failed")
    return _run(
        [_python(), _script("scripts/runtime/execute_workflow.py"), "--dry-run"],
        input_text=plan_json,
    )


def cmd_status(_args: list[str]) -> int:
    """Show active workflows and HITL queue."""
    try:
        from scripts.ui.operator_console import print_status_table
        print_status_table()
        return 0
    except ImportError:
        pass

    # Fallback: check for execution logs in current directory
    logs = list(Path(".").glob("execution_log_*.json"))
    if not logs:
        print("No workflow execution logs found in current directory.")
        print("Tip: pipe workflow output to a file: apotheon run \"...\" > execution_log.json")
        return 0

    print(f"{'Run ID':<35} {'Status':<20} {'Steps':<8} {'Completed At'}")
    print("-" * 80)
    for log_path in sorted(logs, key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
        try:
            data = json.loads(log_path.read_text())
            steps_done = sum(1 for s in data.get("steps", []) if s.get("status") == "completed")
            total = data.get("total_steps", "?")
            print(
                f"{data.get('run_id', 'unknown'):<35} "
                f"{data.get('status', 'unknown'):<20} "
                f"{steps_done}/{total:<6} "
                f"{data.get('completed_at', '')}"
            )
        except Exception:
            continue
    return 0


def cmd_approve(args: list[str]) -> int:
    """Approve a pending HITL gate."""
    if not args:
        return _err("usage: apotheon approve <run-id> [--reason \"...\"]")
    run_id = args[0]
    reason = " ".join(args[2:]) if len(args) > 2 and args[1] == "--reason" else "Approved via CLI"
    try:
        from scripts.runtime.hitl_handler import approve_workflow
        approve_workflow(run_id, approver=os.environ.get("USER", "operator"), justification=reason)
        print(f"Approved: {run_id}")
        return 0
    except ImportError:
        return _err("hitl_handler not available — is temporalio installed?")
    except Exception as exc:
        return _err(str(exc))


def cmd_reject(args: list[str]) -> int:
    """Reject a pending HITL gate."""
    if not args:
        return _err("usage: apotheon reject <run-id> [--reason \"...\"]")
    run_id = args[0]
    reason = " ".join(args[2:]) if len(args) > 2 and args[1] == "--reason" else "Rejected via CLI"
    try:
        from scripts.runtime.hitl_handler import reject_workflow
        reject_workflow(run_id, approver=os.environ.get("USER", "operator"), reason=reason)
        print(f"Rejected: {run_id}")
        return 0
    except ImportError:
        return _err("hitl_handler not available — is temporalio installed?")
    except Exception as exc:
        return _err(str(exc))


def cmd_logs(args: list[str]) -> int:
    """Show step-by-step output for a workflow run."""
    if not args:
        return _err("usage: apotheon logs <run-id>")
    run_id = args[0]
    candidates = list(Path(".").glob(f"*{run_id}*.json"))
    if not candidates:
        return _err(f"No log file found for run-id: {run_id}")
    data = json.loads(candidates[0].read_text())
    print(f"Run: {data.get('run_id')}  Status: {data.get('status')}")
    print(f"Objective: {data.get('objective')}")
    print()
    for step in data.get("steps", []):
        status_icon = {"completed": "OK", "failed": "FAIL", "error": "ERR", "pending_hitl": "HITL", "dry_run": "~"}.get(step.get("status", ""), "?")
        print(f"  Step {step['step']:>2}: [{status_icon}] {step['skill']:<35} {step.get('duration_ms', 0)}ms")
        if step.get("error"):
            print(f"          Error: {step['error']}")
        if step.get("output") and "--verbose" in args:
            print(f"          Output: {step['output'][:300]}")
    return 0


def cmd_skill(args: list[str]) -> int:
    """Skill subcommands: list, gaps."""
    if not args or args[0] == "list":
        code, out = _capture([_python(), _script("scripts/skills/scan_skills.py"), "--root", str(REPO_ROOT)])
        if code != 0:
            # Fallback: count from filesystem
            skills = sorted(p.parent.name for p in (REPO_ROOT / "skills").rglob("SKILL.md"))
            core = sorted(p.parent.name for p in (REPO_ROOT / "core").rglob("SKILL.md"))
            print(f"Domain skills ({len(skills)}):")
            for s in skills:
                print(f"  {s}")
            print(f"\nCore skills ({len(core)}):")
            for s in core:
                print(f"  {s}")
            return 0
        try:
            data = json.loads(out)
            for skill in data.get("skills", []):
                print(f"  {skill.get('name', ''):<40} {skill.get('maturity', ''):<10} {skill.get('category', '')}")
        except json.JSONDecodeError:
            print(out)
        return 0

    if args[0] == "gaps":
        return _run([_python(), _script("scripts/orchestration/detect_skill_gaps.py"), str(REPO_ROOT)])

    return _err(f"unknown skill subcommand: {args[0]}  (list | gaps)")


def cmd_connector_health(_args: list[str]) -> int:
    """Check connector availability."""
    return _run([_python(), _script("scripts/connectors/health_check.py")])


def cmd_memory(args: list[str]) -> int:
    """Memory subcommands: search, init."""
    if not args:
        return _err("usage: apotheon memory <search \"query\" | init>")

    if args[0] == "init":
        return _run([_python(), _script("scripts/memory/init_collections.py")])

    if args[0] == "search":
        query = " ".join(args[1:])
        if not query:
            return _err("usage: apotheon memory search \"<query>\"")
        return _run([_python(), _script("scripts/memory/retrieve_context.py"), query])

    return _err(f"unknown memory subcommand: {args[0]}  (search | init)")


def cmd_validate(_args: list[str]) -> int:
    """Run all validation checks."""
    checks = [
        ("Skill structure", [_python(), _script("scripts/validation/validate_skill_structure.py"), str(REPO_ROOT)]),
        ("Frontmatter", [_python(), _script("scripts/validation/validate_frontmatter.py"), str(REPO_ROOT)]),
        ("Skill gaps", [_python(), _script("scripts/orchestration/detect_skill_gaps.py"), str(REPO_ROOT)]),
    ]
    all_ok = True
    for name, cmd in checks:
        code, out = _capture(cmd)
        icon = "OK" if code == 0 else "FAIL"
        print(f"  [{icon}] {name}")
        if code != 0:
            print(f"      {out.strip()[:200]}")
            all_ok = False

    print()
    if all_ok:
        print("All validation checks passed.")
    else:
        print("Validation failed — see errors above.")
    return 0 if all_ok else 1


def cmd_bootstrap(_args: list[str]) -> int:
    """Full OS health check."""
    return _run([_python(), _script("scripts/orchestration/autonomous_os_bootstrap.py")])


def cmd_init(_args: list[str]) -> int:
    """Initialize Apotheon for first-time use: DB, Qdrant collections, env check."""
    print("Apotheon init\n")
    steps = []

    # 1. Check required env vars
    missing = [v for v in ("ANTHROPIC_API_KEY",) if not os.environ.get(v)]
    if missing:
        print(f"  [WARN] Missing env vars: {', '.join(missing)}")
        print("         Set them in .env or export before running workflows.")
    else:
        print("  [OK]   Required env vars present")

    # 2. Initialize Qdrant collections
    code, _ = _capture([_python(), _script("scripts/memory/init_collections.py")])
    steps.append(("Qdrant collections", code == 0))

    # 3. Validate skill structure
    code, _ = _capture([_python(), _script("scripts/validation/validate_skill_structure.py"), str(REPO_ROOT)])
    steps.append(("Skill structure valid", code == 0))

    # 4. Validate frontmatter
    code, _ = _capture([_python(), _script("scripts/validation/validate_frontmatter.py"), str(REPO_ROOT)])
    steps.append(("Frontmatter valid", code == 0))

    for name, ok in steps:
        icon = "OK" if ok else "FAIL"
        print(f"  [{icon}]   {name}")

    print()
    all_ok = all(ok for _, ok in steps)
    if all_ok:
        print("Init complete. Run: apotheon dry-run \"<your objective>\"")
    else:
        print("Init completed with warnings. Check failures above.")
    return 0 if all_ok else 1


def cmd_doctor(_args: list[str]) -> int:
    """Diagnose environment health: API keys, services, dependencies."""
    print("Apotheon doctor\n")
    checks = []

    # Python version
    import platform
    py_ok = sys.version_info >= (3, 11)
    checks.append(("Python >= 3.11", py_ok, platform.python_version()))

    # ANTHROPIC_API_KEY
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    checks.append(("ANTHROPIC_API_KEY set", bool(api_key), "set" if api_key else "missing"))

    # Qdrant reachability
    try:
        import urllib.request
        qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        with urllib.request.urlopen(f"{qdrant_url}/readyz", timeout=3):
            qdrant_ok = True
            qdrant_detail = qdrant_url
    except Exception as e:
        qdrant_ok = False
        qdrant_detail = str(e)[:60]
    checks.append(("Qdrant reachable", qdrant_ok, qdrant_detail))

    # Temporal reachability (optional)
    temporal_host = os.environ.get("TEMPORAL_HOST", "localhost:7233")
    import socket
    try:
        host, port = temporal_host.rsplit(":", 1)
        sock = socket.create_connection((host, int(port)), timeout=2)
        sock.close()
        temporal_ok = True
        temporal_detail = temporal_host
    except Exception as e:
        temporal_ok = False
        temporal_detail = str(e)[:60]
    checks.append(("Temporal reachable (optional)", temporal_ok, temporal_detail))

    # Postgres (optional)
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        try:
            import asyncio
            import sqlalchemy
            engine = sqlalchemy.create_engine(db_url.replace("+asyncpg", "").replace("+aiosqlite", ""), pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            db_ok = True
            db_detail = "connected"
        except Exception as e:
            db_ok = False
            db_detail = str(e)[:60]
        checks.append(("Database reachable", db_ok, db_detail))

    # Key Python packages
    for pkg in ("anthropic", "qdrant_client", "fastapi", "sqlalchemy", "prometheus_client"):
        try:
            __import__(pkg)
            checks.append((f"Package: {pkg}", True, "installed"))
        except ImportError:
            checks.append((f"Package: {pkg}", False, "not installed"))

    print(f"  {'Check':<40} {'Status':<6} Detail")
    print("  " + "-" * 70)
    for name, ok, detail in checks:
        icon = "OK  " if ok else "WARN"
        print(f"  [{icon}] {name:<38} {detail}")

    print("\nRecommended fixes:")
    if not py_ok:
        print("  - Install Python 3.11+ and recreate your virtual environment.")
    if not api_key:
        print("  - Set ANTHROPIC_API_KEY before live workflow execution.")
    if not qdrant_ok:
        print("  - Start Qdrant: docker compose up -d qdrant")
    if not temporal_ok:
        print("  - Start Temporal (optional): docker compose up -d temporal temporal-ui")
    missing_pkgs = [name.split(': ')[1] for name, ok, _ in checks if name.startswith("Package: ") and not ok]
    if missing_pkgs:
        print("  - Install missing packages: pip install -e \".[dev]\"")
    print()
    failures = [n for n, ok, _ in checks if not ok]
    if not failures:
        print("All checks passed. Apotheon is healthy.")
    else:
        print(f"{len(failures)} check(s) failed or warned. Review above for details.")
    return 0


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_COMMANDS: dict[str, tuple] = {
    "run":           (cmd_run,              "Plan + execute an SDLC workflow"),
    "gtm":           (cmd_gtm,              "Plan + execute a GTM workflow"),
    "dry-run":       (cmd_dry_run,          "Plan SDLC workflow (no execution)"),
    "gtm-dry-run":   (cmd_gtm_dry_run,      "Plan GTM workflow (no execution)"),
    "status":        (cmd_status,           "Show active workflows and HITL queue"),
    "approve":       (cmd_approve,          "Approve a pending HITL gate"),
    "reject":        (cmd_reject,           "Reject a pending HITL gate"),
    "logs":          (cmd_logs,             "Show step outputs for a run"),
    "skill":         (cmd_skill,            "Skill registry: list | gaps"),
    "connector":     (cmd_connector_health, "Check connector health"),
    "connectors":    (cmd_connectors,       "Connectors: check"),
    "local-apps":    (cmd_local_apps,       "Local apps: check"),
    "memory":        (cmd_memory,           "Memory: search \"query\" | init"),
    "backup":        (cmd_backup,           "Backup: create | restore"),
    "validate":      (cmd_validate,         "Run all validation checks"),
    "bootstrap":     (cmd_bootstrap,        "Full OS bootstrap health check"),
    "init":          (cmd_init,             "First-time setup: DB, Qdrant, env check"),
    "doctor":        (cmd_doctor,           "Diagnose environment health"),
    "diagnostics":   (cmd_diagnostics,      "Generate runtime diagnostics report"),
    "workflows":     (cmd_workflows,        "Workflows: list | run [--execute]"),
    "schedules":     (cmd_schedules,        "Schedules: preview | run-due"),
    "runs":          (cmd_runs,             "Run history: list"),
}


def _print_help() -> None:
    print("Apotheon AI Company OS\n")
    print("Usage: apotheon <command> [args]\n")
    print("Commands:")
    for name, (_, desc) in _COMMANDS.items():
        print(f"  {name:<20} {desc}")
    print("\nExamples:")
    print('  apotheon run "Build a secure REST API"')
    print('  apotheon gtm "Launch to enterprise market"')
    print('  apotheon dry-run "Deploy to production"')
    print("  apotheon status")
    print("  apotheon connector health")
    print("  apotheon connectors check --json")
    print("  apotheon local-apps check --compose-file docker-compose.yml")
    print("  apotheon workflows resume RUN-12345678-abcd1234")
    print("  apotheon schedules repair")
    print("  apotheon backup create --output dist")
    print("  apotheon backup restore --dry-run dist/apotheon-backup.tar.gz")
    print("  apotheon skill gaps")
    print('  apotheon memory search "authentication"')
    print("  apotheon init")
    print("  apotheon doctor")


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        _print_help()
        return 0

    # Handle "connector health" as two-word command
    command = argv[0]
    rest = argv[1:]
    if command == "connector" and rest and rest[0] == "health":
        rest = rest[1:]

    handler_entry = _COMMANDS.get(command)
    if handler_entry is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        _print_help()
        return 1

    handler, _ = handler_entry
    return handler(rest)


if __name__ == "__main__":
    sys.exit(main())
