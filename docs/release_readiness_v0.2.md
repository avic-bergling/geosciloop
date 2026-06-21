# v0.2.0 Release Readiness

This document records the v0.2.0 release cleanup target. It is not a tag and does not push to remote.

## Current Commit

- Implementation baseline before release cleanup: `15d0224 feat: add v0.2 dry-run real-data adapter prototype`
- Release cleanup commit: create after final verification with `git commit -m "chore: prepare v0.2.0 release"`

## Version Metadata Check

- `pyproject.toml`: `version = "0.2.0"`
- `geosciloop/__init__.py`: `__version__ = "0.2.0"`
- Editable install check:

```powershell
python -c "import importlib.metadata as m; assert m.version('geosciloop') == '0.2.0'; print('version ok')"
```

## Commands Run

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

## Test Results

- `pytest -q`: passed, 46 tests passed.
- Tests remain offline and deterministic.
- Tests do not require API keys, credentials, GEE auth, live STAC, OSM downloads, internet access, or external datasets.

## Demo Results

- `uhi_synthetic_demo`: passed, validation hard failures 0.
- `uhi_morphology_synthetic_demo`: passed, validation hard failures 0.
- `uhi_real_pilot_template`: passed, validation hard failures 0.

## Dry-Run Artifact Checks

Expected `outputs/uhi_real_pilot_template/` artifacts:

- `adapter_plan.json`
- `data_source_manifest.json`
- `metadata_validation_report.json`
- `validation_report.json`
- `research_ledger.json`
- `dry_run_report.md`
- `summary.md`
- `benchmark_summary.json`
- `run_log.json`

JSON assertions passed:

- `run_log.json`: `dry_run=true`, `download_performed=false`, `credentials_required=false`, `offline=true`
- `research_ledger.json`: `dry_run=true`, `download_performed=false`, `credentials_required=false`
- `metadata_validation_report.json`: `summary.fail == 0`
- `benchmark_summary.json`: contains `sub_scores`

## Known Warning

The dry-run metadata validation report is expected to include one warning:

- `split_strategy`: random non-spatial split can create spatial leakage risk in future geospatial model evaluation.

This warning is intentional and should remain visible until a spatial/block split design is implemented.

## Offline Guarantee

- Required tests use synthetic data or local fixtures.
- The v0.2 dry-run uses `mock://` hrefs and `tests/fixtures/`.
- No required command downloads live remote-sensing, OSM, or population data.

## No-Live-Dependency Guarantee

- No Google Earth Engine authentication is required.
- No live STAC catalog access is required.
- No live OSM/Overpass access is required.
- No external datasets are required.
- Provider-backed access remains optional future work outside required tests.

## outputs/ Git Hygiene

- `outputs/` must remain ignored by git.
- `outputs/` must not be staged or committed.
- Check before commit:

```powershell
git status --short
git ls-files outputs
```

## Pre-Tag Checklist

- [x] `python -m pip install -e ".[dev]"` passed.
- [x] `pytest -q` passed.
- [x] Both v0.1 offline demos passed with hard failures 0.
- [x] v0.2 dry-run passed with hard failures 0.
- [x] Artifact assertions passed.
- [x] Package metadata reports `geosciloop==0.2.0`.
- [ ] `git status --short` is clean after the release cleanup commit.
- [ ] No `outputs/` files are tracked.
- [ ] Maintainer explicitly approves tag creation.
- [ ] Maintainer explicitly approves push.

## Manual Tag/Push Commands

Only run these after explicit maintainer approval:

```powershell
git tag -a v0.2.0 -m "GeoSciLoop v0.2.0"
git push origin main
git push origin v0.2.0
```
