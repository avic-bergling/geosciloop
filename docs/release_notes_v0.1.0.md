# GeoSciLoop v0.1.0 Release Notes

Release target: `v0.1.0`

## Summary

GeoSciLoop v0.1.0 is an offline deterministic architecture demo for a reproducibility-first remote-sensing/GIS AI-scientist scaffold. It focuses on synthetic Urban Heat Island and morphology demos, deterministic validators, machine-readable provenance, generated reports, and release-friendly offline tests.

## What This Release Is

- An offline deterministic architecture demo.
- A reproducibility-first remote-sensing/GIS AI-scientist scaffold.
- A synthetic UHI workflow with artifact-grounded reports.
- A synthetic morphology UHI workflow with variable role separation.
- A testable baseline for future real-data adapter work.

## What This Release Is Not

- It is not a real-data remote-sensing analysis system.
- It is not a fully autonomous scientist.
- It is not evidence about any real city.
- It does not require or use GEE auth, STAC access, OSM downloads, API keys, credentials, or internet data for tests or demos.
- It does not include LangGraph, Snakemake, Prefect, CrewAI, AutoGen, or another stateful harness.

## Main Capabilities

- `geosciloop run configs/uhi_synthetic_demo.yaml --offline`
- `geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline`
- Offline synthetic data generation with fixed seeds.
- Linear regression and random forest model outputs.
- Deterministic validator suite with pass/warn/fail records.
- Machine-readable `research_ledger.json` and `synthetic_truth.json`.
- Human-readable `report.md` and `summary.md`.
- Decomposed `benchmark_summary.json` as the source of truth for artifact completeness and benchmark-style release checks.
- Optional adapter interfaces for future STAC, GEE, OSM, and provenance work.

## Expected Artifacts

Each offline demo writes:

- `data_manifest.json`
- `synthetic_truth.json`
- `research_plan.yaml`
- `research_ledger.json`
- `validation_report.json`
- `metrics.json`: model metrics, correlations, categorical encoding metadata, variable roles, and split metadata.
- `benchmark_summary.json`: artifact completeness and benchmark quality gate source of truth.
- `report.md`
- `summary.md`
- `run_log.json`
- `tables/synthetic_uhi_data.csv`
- `tables/model_predictions.csv`
- `figures/`

Generated runtime output directories are ignored by git and should be regenerated from configs.

## Known Limitations

- Synthetic relationships are designed for demo validation and are not real-world evidence.
- Random train/test splits over synthetic grid cells produce a spatial leakage warning.
- Morphology predictors can be highly correlated; linear coefficients need caution.
- `building_height` is intentionally treated as mixed/context dependent.
- Real-data quality checks for CRS, raster alignment, NoData, cloud/shadow masking, source versions, and vector completeness are not implemented.

## Verification For Release Candidate

Run before tagging:

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
git status --short
```

Tag only after the verification commands pass and the working tree contains only intentional release files.

## Deferred Work

- v0.2.0: fixture-based real-data adapter prototype with CRS/alignment/NoData/source-provenance checks while preserving offline CI.
- v0.3.0: stateful or DAG harness only after real workflow complexity justifies it.
- Later: broader benchmarks, citation checks, human review, and real-world claim gates.
