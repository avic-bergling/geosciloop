---
name: geospatial-python-validator
description: Use when writing or reviewing Python code for geospatial arrays, remote-sensing indices, tabular scientific data, validators, or model diagnostics.
---

# Geospatial Python Validator

## When to use this skill

Use when Python code reads, creates, validates, or evaluates geospatial, remote-sensing, tabular scientific, or diagnostic outputs.

## What to inspect first

- Input schema and expected columns.
- Existing validation functions and tests.
- Synthetic data ranges and NoData conventions.
- Model metrics, report artifacts, and ledger entries.
- Any CRS, resolution, raster alignment, or spatial split assumptions.

## Required workflow

1. Validate expected columns before computation.
2. Validate NDVI, NDWI, and NDBI are in `[-1, 1]`.
3. Validate LST Celsius values are plausible for the task.
4. Validate density-like fields are non-negative.
5. Validate missing values and NoData handling.
6. Validate model metrics exist before report generation.
7. Treat CRS, resolution, and raster alignment as first-class issues when real geospatial arrays are introduced.
8. Flag spatial leakage risks in future ML workflows.
9. Keep validators deterministic and testable.
10. Do not hide validation warnings.

## Required outputs

- Validator functions or review notes.
- Pass/warn/fail results with clear messages.
- Tests or script checks for deterministic validation behavior when feasible.
- Ledger-ready validation summaries.

## Common failure modes

- Clipping invalid values without reporting warnings.
- Letting missing values silently propagate into metrics.
- Reporting model quality without checking metric availability.
- Ignoring spatial leakage or spatial autocorrelation.
- Treating real raster alignment as a later detail.

## Done criteria

- Invalid ranges, missing columns, missing values, and missing metrics are detected deterministically.
- Warnings are visible to callers and can be recorded in the ledger.
- Tests or offline checks cover the validator behavior when a test framework is available.
