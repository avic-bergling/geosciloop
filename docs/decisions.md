# Decisions

## Decision: v0.1 uses deterministic Python runner, not LangGraph

Status: accepted.

GeoSciLoop v0.1 will use a simple deterministic Python runner or state machine. LangGraph can be reconsidered after the offline UHI workflow, validators, ledger, report, and tests are working.

## Decision: repo-local skills are created before real agent runtime

Status: accepted.

Repo-local skills provide task-specific guidance for Codex sessions before the project adopts a runtime agent harness.

## Decision: validators and ledger are core scientific reliability mechanisms

Status: accepted.

Deterministic validators and a provenance ledger are required to keep scientific claims tied to artifacts, metrics, validation results, and stated limitations.

## Decision: all tests must be offline

Status: accepted.

Tests must not require internet access, secrets, API keys, Google Earth Engine authentication, or external data availability.

## Decision: real GEE/STAC support is deferred to optional adapters

Status: accepted.

Real GEE, STAC, and OSM integrations are deferred to optional adapters after v0.1. Offline synthetic data remains the CI baseline.

## Decision: v0.1 dependencies stay lightweight

Status: accepted.

GeoSciLoop v0.1 depends on numpy, pandas, scikit-learn, matplotlib, and PyYAML for the offline synthetic workflow, plus pytest for development tests. Heavier geospatial, GEE, and orchestration dependencies remain optional future extras.

## Decision: keep the simple runner after harness evaluation

Status: accepted.

After reviewing the current deterministic runner, validators, ledger, reports, benchmark summary, tests, and optional real-data adapter stubs, GeoSciLoop should keep the simple Python runner for now. LangGraph, Snakemake, and Prefect are not justified yet because the current workflow is a single deterministic local pipeline with a clear validation surface and no current need for stateful agent loops, formal file-DAG reruns, or production scheduling.

Future adoption triggers:

- LangGraph: add only when planner/executor/validator/report loops need durable state, retries, revision cycles, or human review.
- Snakemake: add only when real-data workflows need reproducible file-based DAG execution across multiple reusable targets.
- Prefect: add only when scheduled production-style runs, operational retries, monitoring, or deployment concerns exist.

Any future harness must be optional, preserve offline tests, and prove artifact equivalence with the current simple runner before it becomes a recommended path.

## Decision: generated runtime outputs stay out of version control

Status: accepted.

GeoSciLoop v0.1 release artifacts should track source code, configs, tests, docs, and small curated documentation examples only. Full runtime output folders under `outputs/`, pytest temporary directories, build artifacts, editable-install metadata, local virtual environments, and temporary logs are ignored through `.gitignore`.

The reason is practical reproducibility: outputs should be regenerated from configs and commands, not committed as stale release state. If a future release needs sample artifacts, add a deliberately small curated directory such as `docs/example_outputs/` with hand-selected files and document how it was produced.

## Decision: v0.2 uses fixture-backed adapters before live providers

Status: accepted.

GeoSciLoop v0.2 adds real-data workflow planning without requiring live data access. STAC, GEE, OSM, and population-grid sources are represented by local fixtures and dry-run adapter plans. This preserves offline deterministic tests while making CRS, resolution, alignment, NoData, cloud/shadow QA, source provenance, and split strategy first-class metadata checks.

Provider-backed access remains optional future work and must be explicitly configured outside required tests. No new dependencies are required for v0.2. The simple deterministic runner remains the execution path for both v0.1 demos and the v0.2 dry-run.

## Decision: keep v0.3 harness decisions deferred

Status: accepted.

The v0.2 dry-run workflow remains a simple deterministic Python runner. LangGraph, Snakemake, Prefect, CrewAI, AutoGen, and other stateful harnesses are still deferred until real workflow complexity justifies them and an artifact equivalence test surface exists.
