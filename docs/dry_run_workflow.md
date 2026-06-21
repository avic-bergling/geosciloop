# v0.2 Dry-Run Workflow

The v0.2 dry-run workflow plans a real-data Urban Heat Island workflow using fixtures only.

Run:

```powershell
geosciloop run configs/uhi_real_pilot_template.yaml --dry-run
```

The workflow must not authenticate, download data, call live STAC/GEE/OSM services, or require API keys.

## Steps

1. Load `configs/uhi_real_pilot_template.yaml`.
2. Build fixture adapter plans.
3. Load fixture metadata from `tests/fixtures/`.
4. Write `adapter_plan.json`.
5. Write `data_source_manifest.json`.
6. Run metadata validators.
7. Write `metadata_validation_report.json` and `validation_report.json`.
8. Write `dry_run_report.md`.
9. Write `summary.md`.
10. Write `run_log.json`.
11. Write `research_ledger.json`.
12. Write `benchmark_summary.json`.
13. Refresh the ledger with the benchmark summary.

## Output Directory

Default output:

```text
outputs/uhi_real_pilot_template/
```

Runtime outputs remain ignored by git.

## Interpretation Boundary

This dry-run is a planning artifact. It is not evidence about a real city, does not process real data, and does not make real-world UHI claims.
