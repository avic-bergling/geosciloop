# GeoSciLoop v0.1 Evaluation

GeoSciLoop v0.1 uses a lightweight offline evaluator for deterministic demo runs. The evaluator is a GeoSciBench-style quality gate for artifacts and provenance, not a claim that the system performs autonomous scientific discovery.

The workflow writes `benchmark_summary.json` in each output directory. Treat `benchmark_summary.json` as the source of truth for artifact completeness and benchmark-style quality-gate checks.

## Evaluation Layers

The evaluator reports decomposed sub-scores:

- `execution_success`: required artifacts exist and deterministic validators have no hard failures.
- `artifact_completeness`: required files and directories are present. Read this from `benchmark_summary.json`.
- `data_validity`: validation has zero `fail` results.
- `model_metric_availability`: every fitted model records finite `r2`, `rmse`, and `mae`.
- `validator_summary`: pass/warn/fail counts from deterministic validators.
- `report_claim_support`: report claims in `research_ledger.json` have supporting artifacts and evidence.
- `reproducibility_metadata`: required seed, split, variable-role, ledger, and synthetic-truth metadata are present.

Each layer has:

- `score`: deterministic numeric score for that layer.
- `status`: `pass`, `warn`, or `fail`.
- `details`: the evidence used to compute the layer.

GeoSciLoop does not produce a single fake AI Scientist Score. If a future benchmark needs a combined score, it must keep these sub-scores visible and explain the weighting.

## Required Artifacts

The artifact completeness layer checks:

- `data_manifest.json`
- `research_plan.yaml`
- `research_ledger.json`
- `validation_report.json`
- `metrics.json`
- `report.md`
- `summary.md`
- `synthetic_truth.json`
- `run_log.json`
- `figures/`
- `tables/`
- `tables/synthetic_uhi_data.csv`
- `tables/model_predictions.csv`

`benchmark_summary.json` is written by the evaluator, so it is not included in the artifact completeness self-check.

## Reproducibility Metadata

The reproducibility layer checks that the output records:

- fixed `random_seed`
- offline run metadata
- `synthetic_truth.json`
- variable roles
- split metadata
- ledger copies of variable roles, synthetic truth, and split metadata

These checks are designed for the synthetic offline v0.1 workflow. They do not validate real data quality, scientific novelty, external citations, or policy relevance.
