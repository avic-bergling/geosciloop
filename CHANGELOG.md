# Changelog

All notable changes to GeoSciLoop are documented here.

## Unreleased - v0.2.0

Fixture-based real-data adapter prototype release-candidate work.

### Added

- Dry-run real-data planning config template: `configs/uhi_real_pilot_template.yaml`.
- Structured v0.2 schema objects for AOI, time range, data source requests, data source records, manifests, and split strategy.
- Fixture-backed STAC, GEE, OSM, and population-grid adapters that do not authenticate, download, or call live services in required tests.
- Dry-run workflow that writes adapter plans, data source manifest, metadata validation report, ledger, dry-run report, summary, benchmark summary, and run log.
- Metadata validators for CRS, raster resolution, raster alignment, NoData, cloud/shadow QA metadata, source provenance, and spatial split strategy.
- v0.2 dry-run benchmark sub-scores for artifact completeness, manifest completeness, provenance, adapter plans, ledger, reproducibility, disclaimers, and no-live-dependency checks.
- Documentation for v0.2 planning, fixture adapters, metadata validators, dry-run workflow, and release-readiness review.

### Clarified

- v0.2 is a fixture-based prototype for real-data workflow planning, not a live real-data analysis system.
- Required v0.2 tests remain offline and deterministic.
- Real STAC, GEE, OSM, and population-grid access remain optional future/provider-backed work outside required tests.
- v0.2 makes no real-world UHI conclusions and does not make GeoSciLoop a complete autonomous scientist.

### Deferred

- Provider-backed live data access, downloads, and authentication.
- Raster/vector processing of real external datasets.
- Spatial/block split implementation for real model evaluation.
- v0.3 harness decisions, including LangGraph, Snakemake, Prefect, CrewAI, and AutoGen.

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
