# Roadmap

## v0.1: Synthetic UHI workflow

- Deterministic offline Urban Heat Island demo.
- Synthetic data generation or checked-in sample artifacts.
- Validators for data ranges, missing values, metrics, and claim support.
- `research_ledger.json` or equivalent provenance artifact.
- Markdown report generated from artifacts only.
- Offline tests and standard-library validation checks.

## v0.2: Fixture-based real-data adapter prototype

- Fixture-backed STAC, GEE, OSM, and population-grid adapter prototype.
- Dry-run workflow for real-data UHI planning without live data access.
- Data source manifest, metadata validators, dry-run report, ledger, and benchmark summary.
- Offline tests remain the CI baseline.
- The simple deterministic runner remains the execution path.
- Live provider-backed runs require future explicit configuration and documented credentials setup outside tests.

## v0.3: Stateful agent runtime

- Add a stateful harness only after v0.1 reliability is proven.
- Keep v0.3 harness decisions deferred until real workflow complexity justifies them.
- Prefer an explicit state machine first; consider LangGraph for durable planner/executor/validator/report loops when state management becomes necessary.

## v0.4: GeoSciBench

- Add benchmark tasks with decomposed scores for execution, artifact completeness, data validity, model metrics, validator outcomes, report claim support, and reproducibility.

## v0.5: Citation verification and human review

- Add citation checks.
- Add human-in-the-loop review for scientific claims, limitations, and release decisions.
