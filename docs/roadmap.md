# Roadmap

## v0.1: Synthetic UHI workflow

- Deterministic offline Urban Heat Island demo.
- Synthetic data generation or checked-in sample artifacts.
- Validators for data ranges, missing values, metrics, and claim support.
- `research_ledger.json` or equivalent provenance artifact.
- Markdown report generated from artifacts only.
- Offline tests and standard-library validation checks.

## v0.2: Real data adapters

- Optional STAC, GEE, OSM, GHSL, and WorldPop adapters.
- Offline tests remain the CI baseline.
- Real-data runs require explicit configuration and documented credentials setup outside tests.

## v0.3: Stateful agent runtime

- Add a stateful harness only after v0.1 reliability is proven.
- Prefer an explicit state machine first; consider LangGraph for durable planner/executor/validator/report loops when state management becomes necessary.

## v0.4: GeoSciBench

- Add benchmark tasks with decomposed scores for execution, artifact completeness, data validity, model metrics, validator outcomes, report claim support, and reproducibility.

## v0.5: Citation verification and human review

- Add citation checks.
- Add human-in-the-loop review for scientific claims, limitations, and release decisions.
