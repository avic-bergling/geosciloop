# Skills Usage

Repo-local skills live under `.agents/skills`. They provide task-specific workflows for future Codex sessions. `AGENTS.md` contains always-on repository rules; skills contain reusable procedures for narrower work.

## Available skills

- `geospatial-research-planner`: Use for turning a remote-sensing/GIS question into a structured task, hypotheses, data needs, workflow stages, and limitations.
- `geospatial-python-validator`: Use for writing or reviewing Python validation logic for geospatial, remote-sensing, tabular scientific data, and model diagnostics.
- `reproducibility-ledger`: Use for provenance, manifests, logs, artifact tracking, and report claim traceability.
- `benchmark-evaluator`: Use for evaluation logic, tests, scoring, benchmark tasks, and CI checks.
- `scientific-report-writer`: Use for README sections, reports, paper drafts, and scientific summaries generated from artifacts.
- `harness-architect`: Use for decisions about LangGraph, CrewAI, AutoGen, Snakemake, Prefect, Codex subagents, OpenAI Agents SDK, or Codex MCP.

## Example prompts

```text
$geospatial-research-planner turn this UHI question into a task config
$geospatial-python-validator review this workflow for range checks and scientific validity
$reproducibility-ledger add provenance tracking for these artifacts
$benchmark-evaluator add tests and scoring for this workflow
$scientific-report-writer write report.md from these artifacts only
$harness-architect decide whether this change needs LangGraph or a simple runner
```

## Updating skills

Update a skill when future work reveals a repeated failure mode, missing workflow step, or domain-specific rule that does not belong in `AGENTS.md`. Keep each skill concise, task-specific, and testable with `python scripts/check_skills.py`. Put broad project rules in `AGENTS.md`; put task-specific workflows in skills.
