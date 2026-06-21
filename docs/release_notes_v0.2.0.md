# GeoSciLoop v0.2.0 Release Notes

Release target: `v0.2.0`

## Summary

GeoSciLoop v0.2.0 is a fixture-based real-data workflow planning prototype. It does not perform live real-data analysis by default.

This release moves GeoSciLoop beyond synthetic-only demos by adding dry-run planning artifacts for real remote-sensing/GIS data sources while preserving offline, deterministic tests.

## What This Release Is

- A reproducibility-first dry-run planning prototype.
- A fixture-backed adapter layer for STAC, GEE, OSM, and population-grid style sources.
- A metadata validation surface for planned real-data workflows.
- An audit trail for adapter plans, data source manifests, validations, reports, ledgers, and benchmark checks.

## What This Release Is Not

- It is not a live real-data remote-sensing analysis system.
- It does not authenticate to Google Earth Engine.
- It does not call live STAC catalogs or OSM/Overpass endpoints in required tests.
- It does not download external datasets.
- It does not process real raster pixels, vector geometries, or population grids.
- It does not make real-world UHI conclusions.
- It is not a complete autonomous scientist.

## Main Capabilities

- `configs/uhi_real_pilot_template.yaml` dry-run template.
- `--dry-run` CLI support.
- Fixture-backed STAC, GEE, OSM, and population adapters.
- `adapter_plan.json` for planned adapter operations.
- `data_source_manifest.json` for planned source metadata and provenance.
- `metadata_validation_report.json` for CRS, resolution, alignment, NoData, cloud/shadow QA, provenance, and split strategy checks.
- `research_ledger.json` integration for `dry_run`, `download_performed`, and `credentials_required`.
- `dry_run_report.md` and `summary.md`.
- v0.2 dry-run benchmark sub-scores.

## Commands

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

## Expected Artifacts

The dry-run command writes `outputs/uhi_real_pilot_template/`:

- `adapter_plan.json`
- `data_source_manifest.json`
- `metadata_validation_report.json`
- `validation_report.json`
- `research_ledger.json`
- `dry_run_report.md`
- `summary.md`
- `benchmark_summary.json`
- `run_log.json`

`outputs/` remains ignored by git.

## Verification Commands And Expected Results

```powershell
python -m pip install -e ".[dev]"
```

Expected: editable install succeeds and package metadata reports `geosciloop==0.2.0`.

```powershell
pytest -q
```

Expected: 46 tests pass.

```powershell
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

Expected: each command exits successfully with validation hard failures 0.

The dry-run metadata validation report is expected to have:

- `fail=0`
- `pass=6`
- `warn=1`

The expected warning is the random non-spatial split warning, which documents spatial leakage risk before any future real geospatial modeling.

## Known Limitations

- Fixture metadata is representative planning metadata, not authoritative provider metadata.
- No live provider queries are performed by default.
- No real raster loading or processing is implemented.
- No actual cloud masking is performed.
- No spatial-block split implementation is used in the dry-run template.
- No real-world claim gates or citation verification are implemented.

## Deferred v0.3 Work

- Live provider-backed STAC/GEE/OSM execution only after explicit user configuration.
- Real raster/vector loading and quality validation.
- Actual cloud/shadow masking and sensor-specific preprocessing.
- Spatial/block split implementation for geospatial model evaluation.
- Harness evaluation only if real workflow complexity justifies LangGraph, Snakemake, Prefect, or another runner.
- Real-world claim gates and citation verification.
