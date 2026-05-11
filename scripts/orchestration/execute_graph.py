from __future__ import annotations

import argparse
import json
from pathlib import Path
import importlib.util
import sys


def _load_executor(root: Path):
    path = root / "core" / "executor" / "graph_executor.py"
    spec = importlib.util.spec_from_file_location("graph_executor", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.GraphExecutor


def task_handler(node, memory):
    produce = node.get("produce", {})
    fail_until = int(node.get("fail_until", 0))
    attempt = memory.get(f"attempt:{node['id']}", 0) + 1
    memory[f"attempt:{node['id']}"] = attempt
    if attempt <= fail_until:
        return {"ok": False}
    return {"ok": True, "memory": produce}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_path", type=Path)
    parser.add_argument("--state-path", type=Path)
    parser.add_argument("--checkpoint-path", type=Path)
    args = parser.parse_args()

    graph = json.loads(args.graph_path.read_text(encoding="utf-8"))
    state = {}
    if args.state_path and args.state_path.exists():
        state = json.loads(args.state_path.read_text(encoding="utf-8"))

    GraphExecutor = _load_executor(Path(__file__).resolve().parents[2])
    executor = GraphExecutor({"task": task_handler})
    result = executor.run(graph, state)

    if args.checkpoint_path:
        args.checkpoint_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
