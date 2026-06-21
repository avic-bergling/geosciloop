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
