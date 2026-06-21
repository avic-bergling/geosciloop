# Changelog

All notable changes to GeoSciLoop are documented here.

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
