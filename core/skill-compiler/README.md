# Skill Compiler

Deterministic scaffold for compiling skill manifests into runnable package artifacts.

## Components
- `compiler.py`: compile entrypoint and activity stub generation.
- `schema_bindings.py`: typed bindings for compiled skill payload.
- `governance.py`: governance wrapper hooks.
- `telemetry.py`: telemetry/rate-limit/cost stubs.
- `tests/test_compiler.py`: deterministic unit tests.

## Run
```bash
python scripts/skill_pipeline.py --version 0.1.0
python -m unittest core.skill-compiler.tests.test_compiler
```
