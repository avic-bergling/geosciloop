# Harness Evaluation

Audit date: 2026-06-21

## Recommendation

Keep the current simple deterministic runner for GeoSciLoop v0.1. Do not add LangGraph, Snakemake, or Prefect yet.

The repository has one real workflow path: a local offline UHI pipeline. It has useful validation surfaces around config parsing, deterministic synthetic data, validators, ledger, reports, summary, split metadata, synthetic truth, and decomposed benchmark output. It does not yet have multiple real-data workflows, repeated file targets, durable agent state, production scheduling, or recovery needs that justify another orchestration dependency.

## Current State Reviewed

- Runner: `geosciloop.core.runner.run_config` routes only `urban_heat_island` and rejects non-offline runs.
- Workflow: `geosciloop.workflows.urban_heat_island.run_uhi_workflow` executes a fixed local sequence from plan to artifacts.
- Validators: deterministic schema, value range, missing value, metric, encoding, spatial split, risk-indicator, multicollinearity, and claim-support checks.
- Ledger: records config, hypotheses, manifest, workflow steps, validation, metrics, warnings, claims, variable roles, synthetic truth, and split metadata.
- Reports: `report.md` and `summary.md` are generated and mark synthetic limitations.
- Evaluator: writes decomposed `benchmark_summary.json`; it does not produce a single fake AI Scientist score.
- Real-data adapters: STAC, GEE, OSM, and provenance helpers exist, but only as optional interfaces tested with injected clients or stubs.
- Tests: local pytest coverage exists for config parsing, synthetic data, validators, workflow artifacts, evaluator behavior, CLI smoke, and adapter stubs.

## Decision Matrix

| Option | Decision | Rationale | Adoption trigger |
| --- | --- | --- | --- |
| Simple deterministic runner | Keep now | Matches the single offline workflow and keeps failures easy to diagnose | Continue until real workflow complexity exceeds a fixed local pipeline |
| LangGraph | Defer | No current durable agent state, retry loop, revision loop, or human-review state machine exists | Add only when planner/executor/validator/report loops need persistent state and tests can assert transitions offline |
| Snakemake | Defer | No real-data file DAG with repeated reusable targets exists | Add when real-data preprocessing, tiling, alignment, modeling, and reporting need file-based partial reruns |
| Prefect | Defer | No scheduled production-style runs or operational monitoring needs exist | Add when recurring jobs, retries, deployment targets, or operational observability become concrete requirements |

## Required Validation Surface Before Any Harness

Before adopting a harness, GeoSciLoop should have:

- At least two workflow task types or one real-data workflow with multiple reusable file targets.
- Stable artifact contracts for manifests, metrics, validation, ledger, report, summary, and benchmark outputs.
- Offline tests proving the harness writes equivalent artifacts to the current runner.
- Clear failure modes that the simple runner cannot handle.
- Optional dependency isolation so base install and offline CI remain unchanged.

## Final Decision

No new harness should be added for the current milestone. The next appropriate work is not LangGraph, Snakemake, or Prefect; it is stronger real-data fixture validation while preserving the current offline runner.
