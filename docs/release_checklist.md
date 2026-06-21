# Release Checklist

Use this checklist before creating a `v0.1.0` tag.

## Scope

- [ ] Confirm the release is scoped to the offline deterministic architecture demo.
- [ ] Confirm no real-data end-to-end workflow was added.
- [ ] Confirm no LangGraph, Snakemake, Prefect, CrewAI, AutoGen, or other harness dependency was added.
- [ ] Confirm tests and demos require no API keys, credentials, GEE auth, STAC access, OSM downloads, or internet data.
- [ ] Confirm generated `outputs/` folders are ignored and not staged.

## Documentation

- [ ] Review `README.md`.
- [ ] Review `CHANGELOG.md`.
- [ ] Review `docs/release_notes_v0.1.0.md`.
- [ ] Review `docs/release_readiness.md`.
- [ ] Confirm docs state that v0.1.0 is synthetic, offline, and not a fully autonomous scientist.

## Verification

Run:

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
geosciloop run configs/uhi_morphology_synthetic_demo.yaml --offline
git status --short
```

Expected:

- `pytest -q` passes.
- Both demo commands exit with validation hard failures `0`.
- `git status --short` shows only intentional release files before commit.
- After commit, `git status --short` is empty before tagging.

## Tagging

Do not tag until the user explicitly chooses to tag.

Suggested manual commands after final review:

```powershell
git add .
git commit -m "chore: prepare v0.1.0 release"
git status --short
git tag -a v0.1.0 -m "GeoSciLoop v0.1.0"
git push origin main
git push origin v0.1.0
```
