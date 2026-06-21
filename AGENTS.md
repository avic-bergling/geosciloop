# GeoSciLoop Agent Guide

## Project mission

GeoSciLoop is a reproducibility-first remote-sensing/GIS AI-scientist framework. Version 0.1 prioritizes an offline deterministic Urban Heat Island workflow before any real GEE, STAC, OSM, or multi-agent runtime. Do not claim GeoSciLoop performs full autonomous scientific discovery.

## Non-negotiable rules

- Keep v0.1 offline and reproducible.
- Do not require API keys, credentials, Google Earth Engine authentication, or internet access for tests.
- Prefer deterministic validators over LLM judgment.
- Tie every scientific claim in generated reports to an artifact, metric, validation result, or explicitly mark it as a hypothesis or limitation.
- Do not overstate correlation as causation.
- Preserve small, fast tests.
- If adding dependencies, justify them in `docs/decisions.md`.
- Run relevant tests after code changes when feasible.

## Development workflow

- Inspect existing files before editing.
- Make minimal changes that serve the current goal.
- Add or update tests with behavior changes.
- Keep docs aligned with code and generated artifacts.
- Update `docs/decisions.md` when making architectural choices.

## Remote-sensing/GIS correctness checklist

- Check CRS/projection assumptions.
- Track raster alignment and resolution.
- Handle NoData and missing values explicitly.
- Validate NDVI, NDWI, and NDBI values are in `[-1, 1]`.
- Validate LST values are in a plausible Celsius range.
- State cloud, shadow, and missing-data caveats.
- Avoid spatial leakage in modeling and evaluation.
- Mention spatial autocorrelation caveats when interpreting metrics.
- Remember that LST is not the same as air temperature.

## Preferred validation commands

Use these when the corresponding package, dev extras, and CLI exist:

```powershell
python -m pip install -e ".[dev]"
pytest -q
geosciloop run configs/uhi_synthetic_demo.yaml --offline
```

Until those are implemented, prefer current offline checks such as:

```powershell
python scripts\check_skills.py
```
