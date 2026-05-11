from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml


@dataclass
class SkillNode:
    name: str
    path: str
    kind: str
    use_when: list[str]
    dependencies: list[str]
    tools: list[str]
    policies: list[str]
    connectors: list[str]
    memory_requirements: list[str]


class SkillGraphEngine:
    """Build and query a planner-consumable skill graph."""

    MANIFEST_GLOBS = ("core/*/SKILL.md", "skills/*/SKILL.md", "agents/*/SKILL.md")

    def __init__(self, root: Path) -> None:
        self.root = root
        self.nodes: dict[str, SkillNode] = {}
        self.edges: list[dict[str, Any]] = []

    def _parse_frontmatter(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return {}
        return yaml.safe_load(text.split("---", 2)[1]) or {}

    def _extract_list(self, fm: dict[str, Any], *keys: str) -> list[str]:
        value: Any = fm
        for key in keys:
            if not isinstance(value, dict):
                return []
            value = value.get(key)
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [v for v in value if isinstance(v, str) and v.strip()]
        return []

    def build(self) -> dict[str, Any]:
        manifests: list[Path] = []
        for pattern in self.MANIFEST_GLOBS:
            manifests.extend(sorted(self.root.glob(pattern)))

        for manifest in manifests:
            fm = self._parse_frontmatter(manifest)
            name = str(fm.get("name") or manifest.parent.name)
            rel = manifest.parent.relative_to(self.root).as_posix()
            kind = rel.split("/", 1)[0].rstrip("s")

            metadata = fm.get("metadata") or {}
            dependencies = self._extract_list(metadata, "dependencies") or self._extract_list(fm, "dependencies")
            tools = self._extract_list(metadata, "tools")
            policies = self._extract_list(metadata, "policies") or self._extract_list(metadata, "governance", "policies")
            connectors = self._extract_list(metadata, "connectors")
            memory_requirements = self._extract_list(metadata, "memory_requirements")
            use_when = self._extract_list(fm, "use_when")

            node = SkillNode(name, rel, kind, use_when, dependencies, tools, policies, connectors, memory_requirements)
            self.nodes[name] = node

        for node in self.nodes.values():
            for dep in node.dependencies:
                self.edges.append({"from": node.name, "to": dep, "resolved": dep in self.nodes})

        return self.as_dict()

    def _detect_cycles(self) -> list[list[str]]:
        graph = {name: [d for d in node.dependencies if d in self.nodes] for name, node in self.nodes.items()}
        visited: set[str] = set()
        stack: list[str] = []
        cycles: list[list[str]] = []

        def dfs(n: str) -> None:
            visited.add(n)
            stack.append(n)
            for nxt in graph.get(n, []):
                if nxt not in visited:
                    dfs(nxt)
                elif nxt in stack:
                    start = stack.index(nxt)
                    cycles.append(stack[start:] + [nxt])
            stack.pop()

        for name in self.nodes:
            if name not in visited:
                dfs(name)
        # de-duplicate cycles by normalized signature
        unique: dict[str, list[str]] = {}
        for cyc in cycles:
            signature = "->".join(sorted(set(cyc)))
            unique[signature] = cyc
        return list(unique.values())

    def _detect_routing_collisions(self) -> list[dict[str, Any]]:
        collisions = []
        keys: dict[str, list[str]] = {}
        for node in self.nodes.values():
            for signal in node.use_when:
                norm = re.sub(r"\s+", " ", signal.strip().lower())
                keys.setdefault(norm, []).append(node.name)
        for signal, owners in keys.items():
            if len(owners) > 1:
                collisions.append({"signal": signal, "skills": sorted(owners)})
        return collisions

    def query_candidates(self, intent: str, required: list[str] | None = None) -> list[dict[str, Any]]:
        intent_l = intent.lower().strip()
        required = required or []
        candidates = []
        for node in self.nodes.values():
            if not any(intent_l in signal.lower() for signal in node.use_when):
                continue
            missing = [dep for dep in node.dependencies if dep not in required and dep not in self.nodes]
            candidates.append({
                "skill": node.name,
                "path": node.path,
                "dependencies": node.dependencies,
                "missing_dependencies": missing,
            })
        return sorted(candidates, key=lambda item: (len(item["missing_dependencies"]), item["skill"]))

    def as_dict(self) -> dict[str, Any]:
        missing = [e for e in self.edges if not e["resolved"]]
        collisions = self._detect_routing_collisions()
        cycles = self._detect_cycles()
        return {
            "nodes": [node.__dict__ for node in sorted(self.nodes.values(), key=lambda n: n.name)],
            "edges": self.edges,
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "missing_dependency_count": len(missing),
                "routing_collision_count": len(collisions),
                "cycle_count": len(cycles),
            },
            "diagnostics": {
                "missing_dependencies": missing,
                "routing_collisions": collisions,
                "cycles": cycles,
            },
            "query_interface": {
                "function": "query_candidates(intent: str, required: list[str] | None = None)",
                "returns": "Sorted candidate skills with dependency diagnostics for planner use",
            },
        }

    def write_reports(self, reports_dir: Path) -> None:
        graph = self.as_dict()
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "skill_graph.json").write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
        mmd = ["graph TD"]
        for n in graph["nodes"]:
            sid = re.sub(r"[^A-Za-z0-9_]", "_", n["name"])
            mmd.append(f"  {sid}[\"{n['name']}\"]")
        for e in graph["edges"]:
            a = re.sub(r"[^A-Za-z0-9_]", "_", e["from"])
            b = re.sub(r"[^A-Za-z0-9_]", "_", e["to"])
            mmd.append(f"  {a}{' --> ' if e['resolved'] else ' -.-> '}{b}")
        (reports_dir / "skill_graph.mmd").write_text("\n".join(mmd) + "\n", encoding="utf-8")

        md = [
            "# Skill Graph Report",
            "",
            f"- Nodes: {graph['stats']['node_count']}",
            f"- Edges: {graph['stats']['edge_count']}",
            f"- Missing dependencies: {graph['stats']['missing_dependency_count']}",
            f"- Routing collisions: {graph['stats']['routing_collision_count']}",
            f"- Cycles: {graph['stats']['cycle_count']}",
            "",
            "## Planner Query Interface",
            "- `query_candidates(intent, required=None)`",
        ]
        (reports_dir / "skill_graph.md").write_text("\n".join(md) + "\n", encoding="utf-8")
