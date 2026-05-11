# AI OS Architecture

Apotheon is organized as a local-first AI operating system with five planes:

1. **Experience plane** (`cli.py`, Streamlit dashboards/UIs)
2. **Orchestration plane** (`scripts/orchestration/*`, workflow schemas)
3. **Governance plane** (`scripts/governance/*`, policy docs)
4. **Execution plane** (`scripts/runtime/*`, schedules, connectors)
5. **Memory plane** (Qdrant, memory scripts, knowledge graph references)

## Diagram pointers

- High-level diagrams: `docs/architecture/diagrams.md`
- Runtime components: `docs/architecture/runtime-components.md`
- Memory architecture: `docs/architecture/memory-engine.md`
