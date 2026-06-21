# Validators

GeoSciLoop validators are deterministic checks that produce pass/warn/fail records in `validation_report.json`.

## `check_config_schema`

Checks that the task config includes required v0.1 fields such as project name, task type, research question, AOI, date range, target variable, explanatory variables, models, output directory, random seed, and offline flag.

## `check_value_ranges`

Checks:

- NDVI, NDWI, and NDBI are in `[-1, 1]`.
- `lst_celsius` is within `[-30, 80]`.
- `population_density`, `road_density`, and `building_density` are non-negative.
- All checked numeric fields are numeric and finite.
- Implausibly high synthetic density values produce warnings rather than hidden clipping.

## `check_missing_values`

Fails if any data column contains missing values.

## `check_model_metrics_exist`

Checks each model has:

- R2
- RMSE
- MAE

It also checks that metrics are finite, R2 is in `[-1, 1]`, and RMSE/MAE are non-negative. Variable importance and coefficients are recorded when available but are not required for every model.

## `check_conclusion_support`

Checks report claims against metric evidence. The v0.1 implementation supports a deterministic check for the claim that NDVI is negatively associated with LST. It also warns on causal language unless a future causal design is recorded.
It also checks positive association claims for NDBI, building density, population density, and road density when those claims appear in report text. A workflow without a recorded causal design emits a warning so future reports do not drift into causal wording.

## Validation philosophy

Validators are the scientific guardrails. They are intentionally narrower than an LLM critic and should be extended whenever the project adds a new data source, model family, or report claim type.
