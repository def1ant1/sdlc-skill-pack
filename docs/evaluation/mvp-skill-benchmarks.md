# MVP Skill Benchmark Regression Checks

The benchmark harness for MVP skills is:

- `scripts/evals/run_skill_benchmarks.py`

## Current MVP benchmark set

- `cash-flow-forecasting`
- `financial-management`
- `revenue-leakage-detection`
- `process-optimization-phase-pack`
- `finance-accounting-phase-pack`

## Usage

```bash
python scripts/evals/run_skill_benchmarks.py
```

The command writes `reports/skill_benchmark_results.json` and exits non-zero if any skill regresses below its baseline threshold.
