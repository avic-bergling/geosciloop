---
name: geospatial-research-planner
description: Use when turning a remote-sensing or GIS research question into a structured research task, plan, hypotheses, data needs, workflow stages, or limitations.
---

# Geospatial Research Planner

## When to use this skill

Use for remote-sensing/GIS research planning, especially Urban Heat Island, land-use classification, change detection, flood or fire mapping, and ecological indicator analysis. For v0.1, prefer a synthetic offline UHI demo.

## What to inspect first

- Existing configs, docs, and generated artifacts.
- Available offline data or synthetic-data generators.
- Existing validators, ledger schema, and report format.
- Whether the task requires real data, and whether that can be deferred.

## Required workflow

1. Convert vague questions into structured config fields.
2. Identify task type: UHI, land-use classification, change detection, flood/fire mapping, or ecological indicator analysis.
3. Fill the planning checklist: AOI, time range, target variable, explanatory variables, spatial unit, candidate data sources, preprocessing, modeling, diagnostics, outputs, and limitations.
4. Record assumptions separately from facts.
5. For real-data future work, separate data source selection from execution.
6. Do not invent citations.

## Required outputs

- Structured task summary or config fields.
- Hypotheses marked as hypotheses.
- Data needs and optional future data sources.
- Workflow stages and validation checkpoints.
- Known limitations and assumptions.

## Common failure modes

- Starting with real GEE/STAC execution before the offline UHI workflow exists.
- Omitting spatial unit, time range, CRS, or target variable.
- Treating LST as air temperature.
- Inventing citations or unsupported background claims.
- Converting correlation language into causal claims.

## Done criteria

- The plan can be executed offline for v0.1 or clearly marks real-data work as deferred.
- Assumptions, hypotheses, data needs, workflow stages, diagnostics, outputs, and limitations are explicit.
- The plan identifies deterministic validators and ledger artifacts needed to support claims.
