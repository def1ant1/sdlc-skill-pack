#!/usr/bin/env python3
"""Route a conversation intent into a next-safe-action decision."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys



def _load_orchestrator_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "core" / "conversation-orchestrator" / "orchestrator.py"
    spec = importlib.util.spec_from_file_location("conversation_orchestrator", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load orchestrator module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", help="Conversation state JSON string.")
    parser.add_argument("--state-file", help="Path to a JSON state file.")
    parser.add_argument("--stdin", action="store_true", help="Read JSON state from stdin.")
    return parser.parse_args()


def load_state(args: argparse.Namespace) -> dict:
    if args.state:
        return json.loads(args.state)
    if args.state_file:
        return json.loads(Path(args.state_file).read_text(encoding="utf-8"))
    if args.stdin:
        return json.loads(sys.stdin.read())
    raise ValueError("Provide --state, --state-file, or --stdin")


def main() -> int:
    args = parse_args()
    state = load_state(args)
    orchestrator = _load_orchestrator_module()
    result = orchestrator.orchestrate_conversation(state)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
