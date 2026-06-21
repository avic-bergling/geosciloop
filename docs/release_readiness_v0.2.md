# v0.2 Release Readiness

This document describes the release-candidate readiness target for v0.2.0. It is not a release announcement and does not create a tag.

## Required Verification

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

## Readiness Criteria

- Existing v0.1 offline demos still run.
- v0.2 dry-run workflow runs without hard failures.
- Required tests remain offline and deterministic.
- No API keys, credentials, GEE auth, STAC access, OSM downloads, or external datasets are required.
- `data_source_manifest.json` is produced.
- Metadata validation report is produced.
- Research ledger records adapter plans, source manifest, metadata validations, `dry_run=true`, `download_performed=false`, and `credentials_required=false`.
- Dry-run report and summary are produced.
- Benchmark summary includes v0.2 dry-run sub-scores.
- `outputs/` remains ignored and untracked.

## Known Expected Warning

The dry-run template intentionally emits a split-strategy warning because it uses a random non-spatial split for a geospatial AOI. A live real-data workflow should use spatial or block splits.

## Tagging Boundary

Do not create a `v0.2.0` tag or push a release without explicit maintainer approval.
