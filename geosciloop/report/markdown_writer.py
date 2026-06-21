from __future__ import annotations

from typing import Any

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import ValidationResult


def build_report_markdown(
    config: TaskConfig,
    plan: dict[str, Any],
    metrics: dict[str, Any],
    validation_results: list[ValidationResult],
    critic_summary: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    linear = metrics["models"].get("linear_regression", {})
    random_forest = metrics["models"].get("random_forest", {})
    ndvi_coef = linear.get("coefficients", {}).get("ndvi")
    ndvi_corr = metrics.get("correlations", {}).get("ndvi")
    validation_counts = {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }
    claim_definitions = [
        (
            "NDVI is negatively associated with LST in this synthetic run.",
            "ndvi",
            {"linear_coefficient": ndvi_coef, "correlation": ndvi_corr},
        ),
        (
            "NDBI is positively associated with LST in this synthetic run.",
            "ndbi",
            {
                "linear_coefficient": linear.get("coefficients", {}).get("ndbi"),
                "correlation": metrics.get("correlations", {}).get("ndbi"),
            },
        ),
        (
            "building_density is positively associated with LST in this synthetic run.",
            "building_density",
            {
                "linear_coefficient": linear.get("coefficients", {}).get("building_density"),
                "correlation": metrics.get("correlations", {}).get("building_density"),
            },
        ),
    ]
    claims = []
    for claim_text, feature, evidence in claim_definitions:
        supporting_validation = [
            result.message
            for result in validation_results
            if result.status == "pass" and feature in result.message
        ]
        claims.append(
            {
                "claim": claim_text,
                "support_status": "supported" if supporting_validation else "unsupported",
                "supporting_artifacts": ["metrics.json", "validation_report.json"],
                "supporting_validation": supporting_validation,
                "evidence": evidence,
            }
        )
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
        "## Methods",
        "",
        f"- AOI: {config.aoi_name}",
        f"- Spatial unit: {config.grid_size_m} m synthetic grid cells",
        f"- Target variable: `{config.target_variable}`",
        f"- Explanatory variables: {', '.join(config.explanatory_variables)}",
        f"- Models: {', '.join(config.models)}",
        "- Validation: schema, value ranges, missing values, model metrics, and conclusion support.",
        "",
        "## Results",
        "",
    ]
    if linear:
        lines.extend(
            [
                f"- Linear regression R2: {linear['r2']:.3f}; RMSE: {linear['rmse']:.3f}; MAE: {linear['mae']:.3f}.",
                f"- NDVI linear coefficient: {ndvi_coef:.3f}.",
            ]
        )
    if random_forest:
        lines.append(
            f"- Random forest R2: {random_forest['r2']:.3f}; RMSE: {random_forest['rmse']:.3f}; MAE: {random_forest['mae']:.3f}."
        )
    lines.append("- Evidence-backed claims:")
    lines.extend(f"  - {claim['claim']}" for claim in claims if claim["support_status"] == "supported")
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
    lines.extend(
        [
            "",
            "## Next steps",
            "",
            "- Add optional STAC/GEE/OSM adapters behind extras while keeping offline tests.",
            "- Add spatial validation and leakage-aware splits for real geospatial arrays.",
            "- Add citation checking and human review before making real-world claims.",
            "",
            "## Artifact trail",
            "",
            "- `research_ledger.json` records config, hypotheses, data manifest, metrics, validations, outputs, and report claims.",
            "- `metrics.json` records model metrics and association evidence.",
            "- `validation_report.json` records deterministic pass/warn/fail checks.",
        ]
    )
    return "\n".join(lines) + "\n", claims
