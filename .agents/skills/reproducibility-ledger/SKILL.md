---
name: reproducibility-ledger
description: Use when creating or updating provenance, manifests, research ledgers, logs, artifact inventories, or scientific evidence chains.
---

# Reproducibility Ledger

## When to use this skill

Use when a workflow creates artifacts, reports claims, records metrics, or needs reproducible provenance.

## What to inspect first

- Existing `research_ledger.json`, manifests, logs, and report files.
- Task config and hypotheses.
- Data manifest and generated outputs.
- Validator results and model metrics.
- Report claims and their supporting artifacts.

## Required workflow

1. Maintain `research_ledger.json` or an equivalent inspectable JSON/YAML artifact.
2. Record task config, hypotheses, data manifest, workflow steps, metrics, validation results, outputs, report claims, and supporting artifacts.
3. Prefer JSON/YAML artifacts that are easy to diff and inspect.
4. Tie every report claim to metrics, validation results, generated data, or mark it as an assumption, hypothesis, or limitation.
5. Do not let report text become the only source of truth.

## Required outputs

- Ledger entry or schema update.
- Artifact inventory with paths and purpose.
- Validation and metric summary.
- Claim-support mapping for reports.
- Limitations and assumptions.

## Common failure modes

- Writing a polished report without machine-readable provenance.
- Recording output paths but not the config that produced them.
- Losing warnings outside the ledger.
- Mixing hypotheses, validated findings, and limitations.
- Omitting synthetic-data disclosure.

## Done criteria

- A future reviewer can trace each claim from report text to a ledger entry and supporting artifact.
- The ledger records enough config and workflow state to reproduce or diagnose the run.
- Unsupported statements are marked as assumptions, hypotheses, or limitations.
