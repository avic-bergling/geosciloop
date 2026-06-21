# Prompt Completion Matrix

Audit date: 2026-06-21

| Prompt / milestone | Expected deliverables | Actual files found | Tests found | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Skills / Harness layer | `AGENTS.md`, repo-local skills, skill validation script, harness strategy docs | `AGENTS.md`; `.agents/skills/*/SKILL.md`; `scripts/check_skills.py`; `docs/skills_usage.md`; `docs/harness_strategy.md`; `docs/codex_workflow.md`; `docs/decisions.md`; `docs/harness_evaluation.md` | No direct pytest test for skills; `scripts/check_skills.py` exists | Complete | Skills are guidance only, not a runtime harness. Harness decision remains simple runner. |
| Synthetic UHI demo | Offline config, deterministic data generation, CLI run, expected artifacts | `configs/uhi_synthetic_demo.yaml`; `geosciloop/tools/synthetic_data.py`; `geosciloop/workflows/urban_heat_island.py`; `geosciloop/cli.py` | `tests/test_schema.py`; `tests/test_synthetic_data.py`; `tests/test_workflow_uhi.py`; `tests/test_cli.py` | Complete | Original demo is preserved and uses `offline: true`. |
| Validators + Ledger + Report | Deterministic validators, research ledger, report writer, artifact traceability | `geosciloop/validators/*`; `geosciloop/core/ledger.py`; `geosciloop/report/markdown_writer.py`; generated `validation_report.json`, `research_ledger.json`, `report.md` | `tests/test_validators.py`; `tests/test_workflow_uhi.py` | Complete | Ledger records major evidence chain fields and output artifacts. |
| Human-readable summary | `summary.md` generated with readable run explanation | `geosciloop/report/summary_writer.py`; workflow calls `write_summary`; generated `summary.md` | `tests/test_workflow_uhi.py` | Complete | Evaluator checks `summary.md`; ledger outputs now record it as `summary`. |
| Morphology synthetic demo | New offline config and synthetic variables for morphology, zones, exposure, vegetation, built-up, water, and LST | `configs/uhi_morphology_synthetic_demo.yaml`; morphology branch in `geosciloop/tools/synthetic_data.py`; workflow handles generated artifacts | `tests/test_schema.py`; `tests/test_synthetic_data.py`; `tests/test_validators.py`; `tests/test_workflow_uhi.py` | Complete | Results are synthetic and not evidence about any real city. |
| Pre-benchmark hardening | Variable role separation, encoding transparency, spatial leakage warning, multicollinearity warning, synthetic truth, split metadata, artifact completeness | `TaskConfig.variable_roles`; config `predictors` and `risk_indicators`; modeling split metadata; `synthetic_truth.json`; validator additions; evaluator artifact list | `tests/test_schema.py`; `tests/test_validators.py`; `tests/test_workflow_uhi.py`; `tests/test_evaluator.py` | Complete | `population_exposure` is excluded from default model features in the morphology config. |
| Benchmark/evaluator | Decomposed offline evaluator, no fake single AI scientist score, artifact and metadata checks | `geosciloop/benchmark/evaluator.py`; generated `benchmark_summary.json`; `docs/evaluation.md` | `tests/test_evaluator.py`; `tests/test_workflow_uhi.py` | Complete | Evaluator is an engineering quality gate, not a scientific benchmark over real data. |
| Real-data adapters | Optional STAC/GEE/OSM/provenance interfaces without affecting offline tests | `geosciloop/adapters/stac.py`; `geosciloop/adapters/gee.py`; `geosciloop/adapters/osm.py`; `geosciloop/adapters/provenance.py`; `docs/real_data_adapters.md`; `docs/data_sources.md` | `tests/test_real_data_adapters.py` | Partial | Implemented but weakly verified. Tests use fake clients and missing-dependency checks only. No real-data workflow or provider integration test exists. |
| Harness evaluation | Decide whether to add LangGraph, Snakemake, or Prefect | `docs/harness_strategy.md`; `docs/harness_evaluation.md`; `docs/decisions.md`; simple runner in `geosciloop/core/runner.py` | Indirectly covered by workflow/CLI tests | Complete | Recommendation is to keep the deterministic runner. No framework adoption is justified yet. |

## Status Definitions

- Complete: implemented and covered by relevant local tests or validation scripts.
- Partial: some code exists, but the intended end-to-end capability is incomplete or weakly verified.
- Missing: expected files or behavior are absent.
- Documented only: described in docs, but no implementation exists.
