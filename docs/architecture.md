# Architecture

## Why v0.1 is deterministic first

GeoSciLoop v0.1 uses a deterministic Python runner because the project first needs a trustworthy validation surface. The offline UHI demo proves that a natural-language research question can be converted into a structured task, synthetic data workflow, model metrics, validator report, ledger, and artifact-grounded report without network access or credentials.

Complex agent runtimes are deferred because they would make failures harder to diagnose before the basic scientific artifacts are reliable.

## Current v0.1 flow

```text
config -> planner -> synthetic data -> UHI workflow -> validators
-> metrics -> research ledger -> report -> benchmark
```

- `geosciloop.core.schema` parses the task config.
- `geosciloop.agents.planner` creates a deterministic research plan.
- `geosciloop.tools.synthetic_data` creates the synthetic grid table.
- `geosciloop.tools.modeling` fits linear regression and random forest models.
- `geosciloop.validators` create deterministic pass/warn/fail results.
- `geosciloop.core.ledger` records the evidence chain.
- `geosciloop.report` writes Markdown from artifacts only.

## Future integration points

- LLM, Codex, or Claude planning can replace the deterministic planner only after generated plans are checked against the config schema and validators.
- GEE, STAC, OSM, GHSL, and WorldPop adapters should be optional extras and must not affect offline tests.
- LangGraph or an explicit state-machine runtime can be added after v0.1 for stateful planner/executor/critic loops.
- Human review and citation verification should gate any real-world scientific claims.

## Scientific core

Validators and the ledger are the scientific core. Report text is derived from artifacts; it is not the source of truth. Every scientific claim should be tied to metrics, validation results, generated data, references, or marked as a limitation or hypothesis.
