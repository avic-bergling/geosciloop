# Release Readiness

Audit date: 2026-06-21

## Current Decision

GeoSciLoop v0.1.0 is ready for release commit preparation as an offline deterministic architecture demo. It is not ready for an immediate `git tag v0.1.0` while the working tree is dirty. Tag after committing the intentional release files and confirming `git status --short` is empty.

## Verification Commands

| Command | Exit status | Observed result |
| --- | --- | --- |
| `python -m pip install -e ".[dev]"` | 0 | Editable install succeeded for `geosciloop==0.1.0`; dev dependency `pytest` was available. |
| `pytest -q` | 0 | `34` tests passed. |
| `geosciloop run configs\uhi_synthetic_demo.yaml --offline` | 0 | Run completed at `outputs\uhi_synthetic_demo`; validation hard failures: `0`. |
| `geosciloop run configs\uhi_morphology_synthetic_demo.yaml --offline` | 0 | Run completed at `outputs\uhi_morphology_synthetic_demo`; validation hard failures: `0`. |

No command failures were observed in this release cleanup.

## Release Hygiene

- `outputs/` is ignored and should not be committed.
- Python caches, pytest temp files, build artifacts, `*.egg-info`, local virtual environments, logs, and temporary files are ignored.
- Full runtime output folders are regenerated from configs instead of tracked.
- No curated example output directory was added because the generated artifacts are easy to reproduce and the full output folders are runtime state.
- Minimal GitHub Actions CI was added at `.github/workflows/tests.yml`; it installs dev extras and runs `pytest -q` only.

## Generated Output Check

Both offline demo output directories contain:

- `data_manifest.json`
- `metrics.json`
- `validation_report.json`
- `research_ledger.json`
- `research_plan.yaml`
- `run_log.json`
- `report.md`
- `summary.md`
- `synthetic_truth.json`
- `benchmark_summary.json`
- `figures/`
- `tables/synthetic_uhi_data.csv`
- `tables/model_predictions.csv`

The regenerated ledgers record `summary.md` in `research_ledger.outputs`:

- `outputs\uhi_synthetic_demo\summary.md`
- `outputs\uhi_morphology_synthetic_demo\summary.md`

The morphology run recorded validation summary:

- Pass: `21`
- Warn: `5`
- Fail: `0`

Expected morphology warnings:

- Not all allowed `functional_zone` categories are represented; allowed and observed categories are documented.
- Random split is used on spatial grid data; spatial leakage may inflate model performance.
- High predictor correlation detected; multicollinearity may make linear coefficients unstable.
- `building_height` should not be interpreted as a simple directional driver.
- No causal design is recorded; causal language should be avoided.

## v0.1.0 Offline Architecture Demo

Status: ready after committing intentional release changes and confirming a clean working tree.

Evidence:

- Package metadata uses version `0.1.0` in `pyproject.toml`.
- Package `__version__` is `0.1.0`.
- Console script entry point is configured as `geosciloop = geosciloop.cli:main`.
- Editable install succeeds.
- Offline tests pass.
- Original synthetic UHI demo runs.
- Morphology synthetic UHI demo runs.
- Reports and summaries label results as synthetic and avoid real-world claims.
- Evaluator writes decomposed offline sub-scores.
- Base tests and demos do not require GEE, STAC, OSM, API keys, credentials, or internet data.

Remaining pre-tag steps:

- Review the release diff.
- Commit the intentional release files.
- Confirm `git status --short` is empty.
- Create the tag only after the user explicitly chooses to tag.

## Known Limitations

- GeoSciLoop v0.1.0 is an offline deterministic architecture demo, not a real-data remote-sensing analysis system.
- Synthetic UHI outputs are not evidence about any real city.
- Random train/test splitting on synthetic grid cells is intentionally warned as a spatial leakage risk.
- Spatial-block splitting and spatial autocorrelation diagnostics are not implemented.
- Real geospatial quality checks are not implemented: CRS, raster alignment, NoData, cloud/shadow masks, source versions, and vector completeness.
- Optional real-data adapters are tested with fake clients or stubs only.
- No LangGraph, Snakemake, Prefect, CrewAI, AutoGen, or other harness is included.

## Deferred v0.2 Work

- Add a fixture-based real-data adapter prototype that runs offline.
- Validate CRS metadata, raster alignment, NoData handling, source provenance, and split strategy.
- Keep provider-backed STAC/GEE/OSM access optional and outside required tests.
- Define optional dependency extras only when a tested workflow needs them.

## Deferred v0.3 Work

- Revisit stateful agent or DAG orchestration only after real workflow complexity justifies it.
- Add LangGraph only if planner/executor/validator/report loops need durable state or repair cycles.
- Add Snakemake only if file-based real-data DAGs and partial reruns become necessary.
- Add Prefect only for scheduled production-style runs with operational needs.

## Manual Release Commands

After final review:

```powershell
git status --short
git add .
git commit -m "chore: prepare v0.1.0 release"
git status --short
git tag -a v0.1.0 -m "GeoSciLoop v0.1.0"
git push origin main
git push origin v0.1.0
```

Do not run the tag commands until `git status --short` is empty after the release commit.
