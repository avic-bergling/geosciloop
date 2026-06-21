# Paper Plan

Working title: **GeoSciLoop: A Reproducibility-First Closed-Loop Agent Framework for Geospatial Research**

## Framing

GeoSciLoop can be framed as a lightweight reproducibility-first framework for geospatial research automation. The initial contribution is not autonomous discovery; it is a deterministic evidence chain that future LLM or agent components must satisfy.

## Candidate contributions

- A closed-loop geospatial research workflow from task config to report.
- Deterministic validators for geospatial-style tabular data and report claims.
- A research ledger that links config, data manifest, metrics, validation, artifacts, and claims.
- An offline UHI demo that can run in CI without credentials.
- A roadmap for optional real-data and agent-runtime integration.

## Evaluation plan

- Engineering success: installability, CLI execution, artifact completeness, and pytest pass rate.
- Data validity: value ranges, missing values, expected schema, and metric availability.
- Scientific reporting: every claim tied to artifacts or marked as limitation/hypothesis.
- Reproducibility: fixed seed, offline config, and deterministic output structure.
- Future comparison: benchmark tasks inspired by remote-sensing agent evaluation work, without adopting a single opaque score.

## Limitations

- v0.1 uses synthetic data only.
- Results are not evidence about a real city.
- LST is not air temperature.
- Associations are not causal effects.
- GEE/STAC/OSM adapters, citation checking, and human review are deferred.
