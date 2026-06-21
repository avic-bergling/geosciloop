from __future__ import annotations

from typing import Any

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import ValidationResult


ASSOCIATION_CLAIMS = [
    ("ndvi", "NDVI is negatively associated with LST in this synthetic run."),
    ("ndbi", "NDBI is positively associated with LST in this synthetic run."),
    ("ndwi", "NDWI is negatively associated with LST in this synthetic run."),
    ("building_density", "building_density is positively associated with LST in this synthetic run."),
    ("floor_area_ratio", "floor_area_ratio is positively associated with LST in this synthetic run."),
]


def build_preliminary_claims(config: TaskConfig) -> list[str]:
    variables = set(config.predictors)
    return [claim for feature, claim in ASSOCIATION_CLAIMS if feature in variables]


def _feature_evidence(metrics: dict[str, Any], feature: str) -> dict[str, Any]:
    linear = metrics["models"].get("linear_regression", {})
    return {
        "linear_coefficient": linear.get("coefficients", {}).get(feature),
        "correlation": metrics.get("correlations", {}).get(feature),
    }


def _supporting_validation(validation_results: list[ValidationResult], feature: str) -> list[str]:
    return [
        result.message
        for result in validation_results
        if result.status == "pass" and feature in result.message
    ]


def _append_metric_lines(lines: list[str], label: str, metrics: dict[str, Any]) -> None:
    if not metrics:
        return
    lines.append(f"- {label} R2: {metrics['r2']:.3f}; RMSE: {metrics['rmse']:.3f}; MAE: {metrics['mae']:.3f}.")


def build_report_markdown(
    config: TaskConfig,
    plan: dict[str, Any],
    metrics: dict[str, Any],
    validation_results: list[ValidationResult],
    critic_summary: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    linear = metrics["models"].get("linear_regression", {})
    random_forest = metrics["models"].get("random_forest", {})
    validation_counts = {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }
    variables = set(config.predictors)
    variable_roles = config.variable_roles()
    claim_definitions = [
        (claim_text, feature, _feature_evidence(metrics, feature))
        for feature, claim_text in ASSOCIATION_CLAIMS
        if feature in variables
    ]
    if "functional_zone" in variables:
        claim_definitions.append(
            (
                "functional_zone uses allowed synthetic categories and documented one-hot encoding for modeling.",
                "functional_zone",
                metrics.get("feature_encoding", {}).get("functional_zone", {}),
            )
        )
    if "population_exposure" in config.risk_indicators:
        claim_definitions.append(
            (
                "population_exposure is included as a synthetic heat-risk relevance indicator rather than a direct LST claim.",
                "population_exposure",
                {"non_negative_validation": True},
            )
        )

    claims = []
    for claim_text, feature, evidence in claim_definitions:
        supporting_validation = _supporting_validation(validation_results, feature)
        claims.append(
            {
                "claim": claim_text,
                "support_status": "supported" if supporting_validation else "unsupported",
                "supporting_artifacts": ["metrics.json", "validation_report.json"],
                "supporting_validation": supporting_validation,
                "evidence": evidence,
            }
        )
    warnings = [result.message for result in validation_results if result.status == "warn"]
    unsupported = [claim for claim in claims if claim["support_status"] != "supported"]

    lines = [
        f"# GeoSciLoop Report: {config.project_name}",
        "",
        "## Research question",
        "",
        config.research_question,
        "",
        "## Synthetic demo disclaimer",
        "",
        "This v0.1 run uses deterministic synthetic geospatial-style tabular data. It is a reproducibility and architecture demo, not evidence about a real city. LST is land surface temperature and is not the same as air temperature.",
        "",
        "## Variables and methods",
        "",
        f"- AOI: {config.aoi_name}",
        f"- Spatial unit: {config.grid_size_m} m synthetic grid cells",
        f"- Target variable: `{config.target_variable}`",
        f"- Explanatory variables: {', '.join(config.explanatory_variables)}",
        f"- Predictors used for LST modeling: {', '.join(variable_roles['predictors'])}",
        f"- Risk indicators not used as default LST predictors: {', '.join(variable_roles['risk_indicators']) or 'none'}",
        f"- Categorical variables: {', '.join(variable_roles['categorical_variables']) or 'none'}",
        f"- Models: {', '.join(config.models)}",
        "- Validation: schema, value ranges, missing values, model metrics, feature encoding, and conclusion support.",
        f"- Split method: {metrics.get('split_metadata', {}).get('split_method', 'not recorded')}.",
        "",
        "## Model results",
        "",
    ]
    _append_metric_lines(lines, "Linear regression", linear)
    _append_metric_lines(lines, "Random forest", random_forest)
    for feature, encoding in metrics.get("feature_encoding", {}).items():
        encoded_columns = ", ".join(f"`{column}`" for column in encoding.get("encoded_columns", []))
        lines.append(
            f"- Categorical encoding: `{feature}` uses `{encoding.get('method')}`; encoded columns: {encoded_columns}."
        )
    lines.extend(
        [
            "",
            "## Supported claims",
            "",
        ]
    )
    supported_claims = [claim for claim in claims if claim["support_status"] == "supported"]
    lines.extend(f"- {claim['claim']}" for claim in supported_claims)
    if not supported_claims:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Unsupported or warned claims",
            "",
        ]
    )
    if unsupported:
        lines.extend(f"- Unsupported: {claim['claim']}" for claim in unsupported)
    else:
        lines.append("- No unsupported report claims were generated.")
    if warnings:
        lines.extend(f"- Warning: {warning}" for warning in warnings)
    else:
        lines.append("- No validation warnings were generated.")
    lines.extend(
        [
            "",
            "## Validation summary",
            "",
            f"- Pass: {validation_counts['pass']}",
            f"- Warn: {validation_counts['warn']}",
            f"- Fail: {validation_counts['fail']}",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {limitation}" for limitation in critic_summary["limitations"])
    if "building_height" in variables:
        lines.append(
            "- This demo does not reduce building_height to a simple directional heat conclusion; 3D morphology is context dependent."
        )
    lines.extend(
        [
            "",
            "## Future real remote-sensing/GIS mapping",
            "",
            "- Map NDVI, NDBI, NDWI, morphology, functional zones, roads, and population layers to explicit data sources later.",
            "- Keep GEE, STAC, OSM, and population-grid adapters optional and outside v0.1 offline tests.",
            "- Add CRS, raster alignment, NoData, spatial leakage, and spatial autocorrelation checks before using real geospatial arrays.",
            "- Add citation checking and human review before making claims about any real place.",
            "",
            "## Artifact trail",
            "",
            "- `research_ledger.json` records config, hypotheses, data manifest, metrics, validations, warnings, outputs, and report claims.",
            "- `metrics.json` records model metrics and association evidence.",
            "- `validation_report.json` records deterministic pass/warn/fail checks.",
            "- `summary.md` provides a human-readable guide to the generated outputs.",
        ]
    )
    return "\n".join(lines) + "\n", claims
