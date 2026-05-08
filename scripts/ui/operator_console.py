#!/usr/bin/env python3
"""
operator_console.py — Apotheon Operator Console (terminal dashboard).

Displays active workflows, HITL approval queue, connector health,
and recent execution history.

Requires: pip install rich

Usage:
    python scripts/ui/operator_console.py              # one-shot status table
    python scripts/ui/operator_console.py --live       # live auto-refresh (5s)
    python scripts/ui/operator_console.py --hitl       # show HITL queue only
    python scripts/ui/operator_console.py --connectors # connector health only

Also usable as a library:
    from scripts.ui.operator_console import print_status_table
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "local")

_PYTHON = sys.executable


def _try_import_rich():
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.columns import Columns
        from rich.text import Text
        from rich.live import Live
        from rich import box
        return Console, Table, Panel, Columns, Text, Live, box
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def _collect_execution_logs(limit: int = 10) -> list[dict]:
    """Scan CWD and REPO_ROOT for execution log JSON files."""
    logs = []
    for search_dir in [Path("."), REPO_ROOT]:
        for path in sorted(search_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text())
                if "run_id" in data and "skill_chain" in data or "steps" in data:
                    logs.append(data)
                    if len(logs) >= limit:
                        return logs
            except Exception:
                continue
    return logs


def _collect_connector_health() -> list[dict]:
    """Run connector health check and return results."""
    try:
        result = subprocess.run(
            [_PYTHON, str(SCRIPTS / "connectors" / "health_check.py"), "--json"],
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(result.stdout)
    except Exception:
        return []


def _collect_memory_health() -> list[dict]:
    """Run memory health check and return results."""
    try:
        result = subprocess.run(
            [_PYTHON, str(SCRIPTS / "memory" / "check_memory_health.py"), "--json"],
            capture_output=True, text=True, timeout=15,
        )
        return json.loads(result.stdout)
    except Exception:
        return []


def _collect_skill_stats() -> dict:
    """Count skills by category."""
    skills_root = REPO_ROOT / "skills"
    core_root = REPO_ROOT / "core"
    domain = sum(1 for _ in skills_root.rglob("SKILL.md")) if skills_root.exists() else 0
    core = sum(1 for _ in core_root.rglob("SKILL.md")) if core_root.exists() else 0
    return {"domain": domain, "core": core, "total": domain + core}


# ---------------------------------------------------------------------------
# Rich rendering
# ---------------------------------------------------------------------------

def _render_rich(refresh: bool = False, hitl_only: bool = False, connectors_only: bool = False) -> None:
    rich = _try_import_rich()
    if not rich:
        print_status_table()
        return

    Console, Table, Panel, Columns, Text, Live, box = rich
    console = Console()

    def _build_layout():
        sections = []

        # ── Header ──────────────────────────────────────────────────
        skill_stats = _collect_skill_stats()
        header_text = (
            f"[bold cyan]Apotheon AI Company OS[/bold cyan]  "
            f"[dim]Skills: {skill_stats['total']} "
            f"({skill_stats['domain']} domain, {skill_stats['core']} core)  "
            f"Mode: {EXECUTION_MODE}[/dim]"
        )

        if not connectors_only:
            # ── Workflow History ─────────────────────────────────────
            logs = _collect_execution_logs()
            wf_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
            wf_table.add_column("Run ID", style="dim", width=32)
            wf_table.add_column("Status", width=18)
            wf_table.add_column("Progress", width=10)
            wf_table.add_column("Skill", width=28)
            wf_table.add_column("Completed At", width=22)

            status_styles = {
                "completed": "[green]✓ completed[/green]",
                "running": "[yellow]⟳ running[/yellow]",
                "failed": "[red]✗ failed[/red]",
                "paused_for_hitl": "[bold yellow]⏸ HITL PENDING[/bold yellow]",
                "dry_run": "[dim]~ dry_run[/dim]",
                "cancelled_by_hitl": "[red]✗ rejected[/red]",
            }

            hitl_queue = []
            for log in logs:
                status = log.get("status", "unknown")
                steps = log.get("steps", [])
                done = sum(1 for s in steps if s.get("status") == "completed")
                total = log.get("total_steps", len(steps))
                last_skill = steps[-1].get("skill", "") if steps else ""
                status_display = status_styles.get(status, status)

                if status == "paused_for_hitl":
                    hitl_queue.append(log)

                if hitl_only and status != "paused_for_hitl":
                    continue

                wf_table.add_row(
                    log.get("run_id", "?")[:30],
                    status_display,
                    f"{done}/{total}",
                    last_skill[:26],
                    log.get("completed_at", "")[:20],
                )

            if not logs:
                wf_table.add_row("[dim]No workflow logs found[/dim]", "", "", "", "")

            sections.append(Panel(wf_table, title="[bold]Workflow History[/bold]", border_style="blue"))

            # ── HITL Queue ───────────────────────────────────────────
            if hitl_queue:
                hitl_table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
                hitl_table.add_column("Run ID", width=32)
                hitl_table.add_column("Paused at Step", width=16)
                hitl_table.add_column("Approve / Reject")

                for log in hitl_queue:
                    run_id = log.get("run_id", "?")
                    step = log.get("paused_at_step", "?")
                    hitl_table.add_row(
                        run_id,
                        str(step),
                        f"[cyan]apotheon approve {run_id[:16]}...[/cyan]  [red]apotheon reject {run_id[:16]}...[/red]",
                    )

                sections.append(Panel(hitl_table, title="[bold yellow]⏸ HITL Approval Queue[/bold yellow]", border_style="yellow"))

        if not hitl_only:
            # ── Connector Health ─────────────────────────────────────
            connector_results = _collect_connector_health()
            conn_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
            conn_table.add_column("Connector", width=16)
            conn_table.add_column("Status", width=14)
            conn_table.add_column("Latency", width=10)
            conn_table.add_column("Error", width=40)

            status_icons = {"OK": "[green]✓ OK[/green]", "DEGRADED": "[yellow]! DEGRADED[/yellow]",
                            "UNREACHABLE": "[red]✗ UNREACHABLE[/red]", "UNKNOWN": "[dim]? UNKNOWN[/dim]"}

            for r in connector_results:
                latency = f"{r.get('latency_ms', '')}ms" if r.get("latency_ms") else "—"
                error = (r.get("error") or "")[:36]
                conn_table.add_row(
                    r["connector"],
                    status_icons.get(r["status"], r["status"]),
                    latency,
                    f"[dim]{error}[/dim]" if error else "",
                )

            if not connector_results:
                conn_table.add_row("[dim]No connectors configured or secrets not set[/dim]", "", "", "")

            # ── Memory Health ────────────────────────────────────────
            mem_results = _collect_memory_health()
            mem_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
            mem_table.add_column("Check", width=24)
            mem_table.add_column("Status", width=12)
            mem_table.add_column("Detail", width=40)

            mem_icons = {"ok": "[green]✓ ok[/green]", "fail": "[red]✗ fail[/red]",
                         "warn": "[yellow]! warn[/yellow]", "skipped": "[dim]~ skip[/dim]", "fixed": "[green]✓ fixed[/green]"}

            for c in mem_results:
                mem_table.add_row(
                    c["check"],
                    mem_icons.get(c["status"], c["status"]),
                    (c.get("detail") or "")[:38],
                )

            if not mem_results:
                mem_table.add_row("[dim]Memory health check unavailable[/dim]", "", "")

            sections.append(
                Columns([
                    Panel(conn_table, title="[bold]Connector Health[/bold]", border_style="blue"),
                    Panel(mem_table, title="[bold]Memory Layer[/bold]", border_style="blue"),
                ])
            )

        # ── Footer ──────────────────────────────────────────────────
        footer = Text(
            f"  apotheon run \"<objective>\"  |  apotheon approve <run-id>  |  "
            f"apotheon skill gaps  |  apotheon memory search \"<query>\"",
            style="dim",
        )
        sections.append(footer)

        return header_text, sections

    if refresh:
        from rich.live import Live
        with Live(console=console, refresh_per_second=0.2) as live:
            while True:
                header_text, sections = _build_layout()
                console.print(header_text)
                for s in sections:
                    console.print(s)
                time.sleep(5)
                live.console.clear()
    else:
        header_text, sections = _build_layout()
        console.print(header_text)
        for s in sections:
            console.print(s)


# ---------------------------------------------------------------------------
# Plain-text fallback (no rich)
# ---------------------------------------------------------------------------

def print_status_table() -> None:
    """Print a plain-text status summary (no rich dependency)."""
    logs = _collect_execution_logs()
    skill_stats = _collect_skill_stats()

    print(f"\nApotheon Operator Console")
    print(f"Skills: {skill_stats['total']} total | Mode: {EXECUTION_MODE}")
    print()

    if logs:
        print(f"{'Run ID':<34} {'Status':<22} {'Steps':<8} {'Completed At'}")
        print("-" * 80)
        for log in logs:
            steps = log.get("steps", [])
            done = sum(1 for s in steps if s.get("status") == "completed")
            total = log.get("total_steps", len(steps))
            print(
                f"{log.get('run_id', '?')[:32]:<34} "
                f"{log.get('status', '?'):<22} "
                f"{done}/{total:<6} "
                f"{log.get('completed_at', '')[:19]}"
            )
    else:
        print("No workflow logs found.")

    print()
    connector_results = _collect_connector_health()
    if connector_results:
        print(f"{'Connector':<16} {'Status':<14} {'Latency'}")
        print("-" * 45)
        for r in connector_results:
            latency = f"{r.get('latency_ms', '')}ms" if r.get("latency_ms") else "—"
            print(f"{r['connector']:<16} {r['status']:<14} {latency}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Apotheon Operator Console")
    parser.add_argument("--live", action="store_true", help="Auto-refresh every 5 seconds")
    parser.add_argument("--hitl", action="store_true", help="Show HITL queue only")
    parser.add_argument("--connectors", action="store_true", help="Connector health only")
    parser.add_argument("--plain", action="store_true", help="Plain text output (no rich)")
    args = parser.parse_args()

    if args.plain:
        print_status_table()
        return 0

    _render_rich(refresh=args.live, hitl_only=args.hitl, connectors_only=args.connectors)
    return 0


if __name__ == "__main__":
    sys.exit(main())