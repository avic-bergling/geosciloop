# Harness Strategy

## Decision

GeoSciLoop v0.1 should start with a deterministic Python runner instead of LangGraph, CrewAI, or AutoGen. The first milestone needs a small validation surface: a synthetic offline Urban Heat Island task, explicit validators, a provenance ledger, a generated report, and repeatable tests. A complex agent harness before that would make failures harder to diagnose and would encourage generic "AI scientist" claims before the scientific workflow is trustworthy.

## Minimal v0.1 runner

The minimal runner should execute a fixed pipeline:

```text
config -> planner -> workflow -> validators -> ledger -> report -> evaluator
```

It should read a local config, create or load deterministic synthetic data, compute UHI-related indicators, run validators, write `research_ledger.json` or an equivalent artifact, generate a report from artifacts only, and evaluate engineering completeness separately from scientific value.

## When to add LangGraph

Add LangGraph only after the offline demo, validators, ledger, and tests pass. It is appropriate for stateful long-running agent workflows where planning, execution, validation, and revision need durable state transitions.

## When to add Snakemake

Add Snakemake when GeoSciLoop workflows need formal reproducible DAG execution across data preparation, model runs, metrics, reports, and artifact publishing.

## When to add Prefect

Add Prefect when scheduled or production-style data pipelines are needed, especially for monitoring runs, retries, and operational observability.

## When to use Codex subagents

Use Codex subagents only when the user explicitly asks for parallel specialized coding tasks and each output can be reviewed independently. Do not use subagents as a substitute for deterministic validation.

## When to use OpenAI Agents SDK or Codex MCP

Use OpenAI Agents SDK or Codex MCP when an external orchestrator needs to call Codex as one tool among several. Do not add that layer for v0.1 unless there is already a working offline validation surface.

## Staged roadmap

- v0.1: deterministic offline runner.
- v0.2: fixture-backed STAC, GEE, OSM, and population-grid adapter prototype behind the simple runner.
- v0.3: LangGraph stateful agent loop.
- v0.4: GeoSciBench benchmark.
- v0.5: citation checking and human-in-the-loop review.
