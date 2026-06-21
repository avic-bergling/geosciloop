---
name: benchmark-evaluator
description: Use when adding evaluation logic, tests, scoring, benchmark tasks, CI checks, or reproducibility scoring for GeoSciLoop workflows.
---

# Benchmark Evaluator

## When to use this skill

Use when defining benchmark tasks, test gates, scoring criteria, or CI checks for GeoSciLoop.

## What to inspect first

- Existing tests, validation scripts, and CI commands.
- Workflow outputs, ledger schema, reports, and metrics.
- Synthetic data fixtures and deterministic seeds.
- Scientific task definition and expected artifacts.

## Required workflow

1. Separate engineering success from scientific value.
2. Prefer layered metrics: execution success, artifact completeness, data validity, model metric availability, validator pass/warn/fail rate, report claim support, and reproducibility.
3. Avoid one fake "AI Scientist Score" unless it is clearly decomposed.
4. Add pytest tests for deterministic parts when pytest exists.
5. Keep tests offline.
6. Use synthetic data for CI.

## Required outputs

- Evaluation criteria or score decomposition.
- Deterministic checks for expected artifacts.
- Offline tests or validation scripts.
- Clear pass/warn/fail reporting.

## Common failure modes

- Collapsing all quality into one opaque score.
- Treating execution success as scientific validity.
- Requiring network access, credentials, or external datasets in CI.
- Benchmarking report prose without checking artifact support.
- Ignoring reproducibility or deterministic seeds.

## Done criteria

- The evaluator can explain which layer failed and why.
- Offline checks cover deterministic behavior.
- Scientific-value claims remain separate from engineering pass/fail status.
