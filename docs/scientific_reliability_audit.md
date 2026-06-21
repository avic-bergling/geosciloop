# Scientific Reliability Audit

Audit date: 2026-06-21

This audit checks whether the current repository keeps synthetic demonstrations separate from real-world scientific evidence.

## Summary

The offline UHI demos are scientifically disciplined for architecture demonstrations: they label data as synthetic, record variable roles and synthetic generation metadata, avoid causal conclusions, and use deterministic validators. They are not real remote-sensing/GIS science outputs. Real-world reliability remains out of scope until real-data workflows add CRS, raster alignment, NoData, cloud/shadow, data-source, and spatial validation checks.

## Checklist

| Check | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Synthetic demos clearly labeled as synthetic | Pass | `README.md`; `report.md` writer; `summary.md` writer; synthetic data manifests | Reports state the run is not evidence about a real city. |
| Report claims tied to metrics and validation artifacts | Pass | `build_report_markdown`; `research_ledger.report_claims`; evaluator `report_claim_support` | Claims include supporting artifacts and validation evidence. |
| Causal language avoided without causal design | Pass with warnings | `check_conclusion_support` emits "No causal design is recorded"; reports list warnings | Validators warn rather than silently accepting causal language. |
| LST distinguished from air temperature | Pass | `report.md` and `summary.md` text explicitly distinguish LST from air temperature | This is covered by workflow tests. |
| `population_exposure` treated as risk/exposure, not default LST predictor | Pass | Morphology config sets `risk_indicators: [population_exposure]`; tests assert it is absent from model features | Validator warns if a risk indicator is used as a feature. |
| Random spatial splits warned about | Pass | `check_spatial_split_strategy` warning for x/y grid plus random split | This warning is expected for current demos. |
| Multicollinearity/correlation warnings implemented | Pass | `check_predictor_multicollinearity`; workflow tests check high predictor correlation warning | Building-height interpretation is also guarded. |
| Functional-zone encoding transparent | Pass | `feature_encoding.functional_zone` in metrics and manifest | Records allowed, observed, counts, baseline, and encoded columns. |
| Synthetic ground truth recorded | Pass | `synthetic_truth.json`; `data_manifest.synthetic_generation`; ledger copy | Includes formula description, pseudocode, coefficient signs, noise, seed, and role notes. |
| Variable roles explicit | Pass | `TaskConfig.variable_roles`; configs include `target`, `predictors`, `risk_indicators`, `categorical_variables`, `metadata_variables` | Stored in metrics and ledger. |
| Real-world data quality validated | Missing | No real-data workflow exists | Adapter interfaces do not validate real rasters, CRS, cloud masks, or external data quality. |
| Spatial autocorrelation handled beyond warning | Partial | Spatial random split warning exists | No spatial-block split or spatial autocorrelation metric is implemented. |

## Scientific Boundaries

- The current findings are synthetic association checks only.
- The project does not yet support real-world UHI claims.
- The project does not yet validate real satellite data, OSM completeness, GHSL/WorldPop quality, CRS, raster alignment, NoData, or cloud/shadow masks.
- The current evaluator checks reproducibility and artifact completeness, not scientific truth.

## Release Risk

The scientific risk for a v0.1 offline architecture demo is acceptable if release notes clearly state that all results are synthetic. The scientific risk for a v0.2 real-data prototype is still high because adapter interfaces are not wired into an end-to-end real-data workflow and have no provider-backed integration validation.

## Recommended Next Scientific Hardening Goal

Before claiming a real-data prototype, add a tiny offline fixture-based real-data workflow that exercises CRS metadata, raster alignment, NoData handling, data-source provenance, and spatial split strategy without requiring internet or credentials.
