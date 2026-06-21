---
name: harness-architect
description: Use when deciding whether to add LangGraph, CrewAI, AutoGen, Snakemake, Prefect, Codex subagents, OpenAI Agents SDK, Codex MCP, or a simple runner.
---

# Harness Architect

## When to use this skill

Use when evaluating workflow orchestration, agent runtime, pipeline, scheduler, or external tool-calling architecture.

## What to inspect first

- Current offline workflow maturity.
- Validators, ledger, reports, tests, and artifact checks.
- Whether the task needs stateful agent behavior, DAG reproducibility, scheduled pipelines, or parallel coding.
- Existing decisions in `docs/decisions.md`.

## Required workflow

1. Default v0.1 to a simple deterministic Python runner or state machine.
2. Add complex harnesses only after the offline workflow, validators, ledger, and tests work.
3. Recommend LangGraph only for stateful long-running agent workflows after v0.1.
4. Recommend Snakemake for research reproducibility pipelines.
5. Recommend Prefect for production-style data orchestration.
6. Recommend Codex subagents only when delegation or parallel work is explicitly requested, the work streams are decomposed, and outputs can be independently reviewed.
7. Recommend OpenAI Agents SDK or Codex MCP only when orchestration outside Codex itself is needed.
8. Avoid adopting a harness before there is a clear validation surface.

## Required outputs

- Harness recommendation with rationale.
- Deferred options and prerequisites.
- Validation surface required before adoption.
- Decision update for `docs/decisions.md` when architecture changes.

## Common failure modes

- Adding LangGraph, CrewAI, or AutoGen before a working offline workflow.
- Confusing orchestration complexity with scientific reliability.
- Choosing a tool before defining validators and artifacts.
- Using subagents when delegation was not explicitly requested or outputs cannot be independently reviewed.
- Requiring network services for v0.1 tests.

## Done criteria

- The recommendation preserves offline deterministic v0.1 behavior.
- Any new harness has a clear validation surface and documented reason.
- Subagents are recommended only for explicitly requested, decomposed work streams with independently reviewed outputs.
- Deferred tools have explicit triggers for future adoption.
