# GeoSciLoop

GeoSciLoop is a reproducibility-first remote-sensing/GIS workflow scaffold. v0.1.0 is a deterministic offline synthetic Urban Heat Island demo, and v0.2.0 adds a fixture-based real-data adapter prototype for dry-run planning.

It demonstrates a small research loop:

```text
research question -> task config -> research plan -> synthetic data
-> models -> validators -> ledger -> report -> summary -> benchmark summary
```

GeoSciLoop v0.1.0 does not perform full autonomous scientific discovery, does not make real-world UHI claims, and does not require Google Earth Engine, STAC, OSM, API keys, credentials, or internet access for tests or demos.

The v0.2.0 dry-run prototype also remains offline by default. It plans fixture-backed STAC, GEE, OSM, and population-grid metadata but does not download data, authenticate, call live providers, or produce real-world UHI conclusions.

## Quickstart

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

If the console script is unavailable in your shell, use the module entry point:

```powershell
python -m geosciloop.cli run configs/uhi_synthetic_demo.yaml --offline
python -m geosciloop.cli run configs/uhi_morphology_synthetic_demo.yaml --offline
python -m geosciloop.cli run configs/uhi_real_pilot_template.yaml --dry-run
```

## What v0.1.0 Does

- Runs a deterministic offline synthetic UHI workflow.
- Runs a second deterministic morphology UHI demo with building height, floor-area ratio, functional zones, population exposure, vegetation, built-up intensity, and water signal.
- Separates variable roles into target, predictors, risk indicators, categorical variables, and metadata variables.
- Fits linear regression and random forest models on synthetic tabular grid data.
- Writes deterministic validation results for value ranges, missing values, metrics, causal overclaim risk, spatial split leakage risk, categorical encoding, multicollinearity, and claim support.
- Writes machine-readable provenance and audit files, including `research_ledger.json`, `data_manifest.json`, `metrics.json`, `validation_report.json`, `synthetic_truth.json`, and `run_log.json`.
- Writes `report.md` and `summary.md` from artifacts, with synthetic-data disclaimers and limitations.
- Writes a decomposed `benchmark_summary.json` quality gate. Use this file as the source of truth for artifact completeness and benchmark-style release checks.
- Provides optional STAC, GEE, OSM, and provenance adapter interfaces for future work without making them part of the offline v0.1 demo.

## What v0.2.0 Adds

- Dry-run real-data planning through `configs/uhi_real_pilot_template.yaml`.
- Fixture-backed STAC, GEE, OSM, and population-grid adapters.
- Data source manifest generation through `data_source_manifest.json`.
- Metadata validators for CRS, resolution, raster alignment, NoData, cloud/shadow QA, source provenance, and split strategy.
- `dry_run_report.md` and `summary.md` for human-readable dry-run review.
- Decomposed v0.2 benchmark sub-scores for adapter plans, manifest completeness, provenance, ledger completeness, reproducibility, disclaimers, and no-live-dependency checks.

## What v0.2.0 Still Does Not Do

- It does not run live STAC, GEE, OSM, GHSL, WorldPop, or other external provider queries by default.
- It does not perform live data downloads.
- It does not authenticate or require API keys.
- It does not authenticate to Google Earth Engine.
- It does not call live STAC catalogs or live OSM/Overpass endpoints in required tests.
- It does not download real rasters, vectors, or population grids.
- It does not process real pixels or geometries.
- It does not make real-world UHI conclusions.
- It does not add a stateful harness.

## What v0.1.0 Does Not Do

- It is not a real-data remote-sensing analysis system.
- It is not a complete autonomous scientist.
- It does not authenticate to Google Earth Engine.
- It does not download STAC, OSM, GHSL, WorldPop, or other external datasets during tests or demos.
- It does not validate real raster CRS, alignment, NoData, cloud masks, or sensor QA fields.
- It does not prove causal effects.
- It does not treat synthetic LST associations as evidence about any real city.
- It does not use LangGraph, Snakemake, Prefect, CrewAI, AutoGen, or another stateful harness.

## Configs

- `configs/uhi_synthetic_demo.yaml`: original synthetic UHI demo.
- `configs/uhi_morphology_synthetic_demo.yaml`: synthetic morphology demo with functional zones and population exposure as a risk indicator.
- `configs/uhi_real_pilot_template.yaml`: v0.2 fixture-backed dry-run template for real-data workflow planning.

All bundled configs run offline or dry-run locally and write outputs under `outputs/`, which is intentionally ignored by git.

## Output Artifacts

A successful run creates a directory such as `outputs/uhi_morphology_synthetic_demo/`:

```text
data_manifest.json          synthetic data inventory and variable roles
synthetic_truth.json        machine-readable synthetic generation notes
research_plan.yaml          deterministic plan and hypotheses
metrics.json                model metrics, correlations, encoding, and split metadata
validation_report.json      deterministic pass/warn/fail checks
research_ledger.json        config, data, metrics, validations, warnings, claims, outputs
benchmark_summary.json      artifact completeness and benchmark quality gate
report.md                   artifact-grounded scientific-style report
summary.md                  human-readable output guide
run_log.json                run metadata and hard failures
tables/                     generated CSV tables
figures/                    generated diagnostic figures
```

The JSON/YAML artifacts are the audit source of truth. The Markdown files are generated views over those artifacts.

The v0.2 dry-run creates `outputs/uhi_real_pilot_template/` with:

```text
adapter_plan.json                 fixture adapter plans
data_source_manifest.json         planned source metadata and provenance
metadata_validation_report.json   CRS, resolution, alignment, NoData, QA, provenance, split checks
validation_report.json            same pass/warn/fail records for unified consumers
research_ledger.json              config, source requests, plans, manifest, validations, outputs
benchmark_summary.json            decomposed v0.2 dry-run quality gate
dry_run_report.md                 human-readable dry-run report
summary.md                        human-readable output index
run_log.json                      dry-run status and no-live-dependency flags
```

## Project Status

GeoSciLoop v0.1.0 has been tagged and published as an offline deterministic architecture demo. It is not yet ready to be described as a real-data UHI analysis system.

GeoSciLoop v0.2.0 has been tagged and published as a fixture-based real-data workflow planning prototype. It remains a dry-run/fixture-based system by default and does not perform live real-data remote-sensing analysis unless future provider-backed adapters are explicitly configured.

See:

- `docs/project_status.md`
- `docs/scientific_reliability_audit.md`
- `docs/release_readiness.md`
- `docs/release_notes_v0.1.0.md`
- `docs/release_readiness_v0.2.md`
- `docs/release_notes_v0.2.0.md`

## Development And Validation

Run the local checks:

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

The tests are designed to be offline and fast. Do not add tests that require API keys, GEE auth, STAC access, OSM downloads, or live internet data.

## Roadmap

- v0.1.0: offline deterministic architecture demo with synthetic UHI and morphology workflows, validators, ledger, reports, summary, and decomposed evaluator.
- v0.2.0: fixture-based real-data adapter prototype that preserves offline CI and validates CRS, raster alignment, NoData, source provenance, and split strategy.
- v0.3.0: stateful agent or workflow harness prototype only after real workflow complexity justifies it.
- Later: broader benchmark tasks, citation checking, human review, and real-world scientific claim gates.
