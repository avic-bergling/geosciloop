---
name: scientific-report-writer
description: Use when writing README sections, reports, paper drafts, scientific summaries, methods, results, limitations, or next-step sections from artifacts.
---

# Scientific Report Writer

## When to use this skill

Use when generating Markdown reports, README scientific summaries, paper-style drafts, or result narratives.

## What to inspect first

- Ledger, metrics, validation summaries, and output artifacts.
- Task config, hypotheses, and data manifest.
- Whether data are synthetic or real.
- Known caveats about LST, cloud/missing data, spatial leakage, and spatial autocorrelation.
- Available references; do not fabricate missing references.

## Required workflow

1. Write from artifacts only.
2. Include methods, results, validation summary, limitations, and next steps.
3. Clearly state when data are synthetic.
4. Avoid causal claims without causal design.
5. Distinguish LST from air temperature.
6. Do not fabricate references.
7. Include reproducibility details.
8. Prefer clear Markdown.

## Required outputs

- Report or documentation section in Markdown.
- Methods and inputs summary.
- Results tied to metrics or artifacts.
- Validation summary.
- Limitations and next steps.
- Reproducibility notes.

## Common failure modes

- Turning synthetic demo findings into real-world claims.
- Presenting correlation as causation.
- Treating LST as air temperature.
- Citing papers that were not provided or verified.
- Omitting failed or warning validation results.

## Done criteria

- Every scientific claim is supported by an artifact, metric, validation result, or is marked as hypothesis/limitation.
- Synthetic data and reproducibility limits are explicit.
- The report can be audited against the ledger.
