# Changelog

All notable changes to GeoSciLoop are documented here.

## 0.2.0 - 2026-06-21

Fixture-based real-data workflow planning prototype.

### Added

- Fixture-based real-data adapter prototype.
- Dry-run workflow for `configs/uhi_real_pilot_template.yaml`.
- `adapter_plan.json` artifact.
- `data_source_manifest.json`.
- `metadata_validation_report.json`.
- `dry_run_report.md` and `summary.md`.
- Research ledger integration for `dry_run`, `download_performed`, and `credentials_required`.
- Metadata validators for CRS, resolution, alignment, NoData, cloud/shadow QA, provenance, and split strategy.
- Decomposed benchmark sub-scores for the v0.2 dry-run.
- Fixture-backed STAC, GEE, OSM, and population adapters.
- Offline tests for adapters, validators, workflow, and evaluator.

### Clarified

- v0.2 does not perform live real-data analysis by default.
- v0.2 does not require GEE, STAC, OSM, API keys, credentials, internet, or external datasets for tests.
- v0.2 does not make real-world scientific claims.

### Deferred

- Live STAC/GEE/OSM provider-backed execution.
- Real raster loading and processing.
- Actual cloud masking.
- Actual spatial-block split implementation.
- LangGraph, Snakemake, Prefect, or other harness adoption.
- Real-world claim gates and citation verification.

## 0.1.0 - 2026-06-21

Initial offline deterministic architecture demo release candidate.

### Added

- Offline synthetic Urban Heat Island workflow.
- Offline synthetic morphology UHI workflow with building height, floor-area ratio, functional zones, population exposure, NDVI, NDBI, NDWI, and synthetic LST.
- Config schema with explicit variable roles: target, predictors, risk indicators, categorical variables, and metadata variables.
- Deterministic validators for schema, value ranges, missing values, model metrics, functional-zone encoding, random spatial split leakage, risk-indicator misuse, multicollinearity, building-height interpretation, and claim support.
- Research ledger, data manifest, metrics, validation report, run log, synthetic truth metadata, report, summary, figures, and tables.
- Decomposed offline benchmark summary for artifact completeness, reproducibility metadata, model metrics, validator status, and report claim support.
- Optional STAC, Google Earth Engine, OSM, and provenance adapter interfaces for future work, tested only with offline fakes or stubs.
- Repo-local agent guidance and release-readiness documentation.
- Minimal GitHub Actions test workflow.

### Clarified

- GeoSciLoop v0.1.0 is not a real-data remote-sensing analysis system.
- GeoSciLoop v0.1.0 is not a complete autonomous scientist.
- Synthetic outputs are not evidence about any real city.
- Base tests and demos require no API keys, credentials, GEE authentication, STAC access, OSM downloads, or internet data.

### Deferred

- End-to-end real-data workflows.
- Real raster/vector validation for CRS, alignment, NoData, cloud/shadow masks, and source quality.
- LangGraph, Snakemake, Prefect, CrewAI, AutoGen, and other orchestration frameworks.
- Real-world scientific claims and citation-gated review.
