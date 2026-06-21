from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import ValidationResult


REQUIRED_METRICS = ["r2", "rmse", "mae"]
MULTICOLLINEARITY_THRESHOLD = 0.85


def check_model_metrics_exist(metrics: dict[str, dict[str, Any]]) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    for model_name, model_metrics in metrics.items():
        missing = [metric for metric in REQUIRED_METRICS if metric not in model_metrics]
        if missing:
            results.append(
                ValidationResult(
                    "model_metrics",
                    "fail",
                    f"{model_name} missing required metric(s): {', '.join(missing)}",
                    {"model": model_name, "missing": missing},
                )
            )
            continue

        invalid_values: list[str] = []
        for metric in REQUIRED_METRICS:
            value = model_metrics[metric]
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                invalid_values.append(metric)
        has_failure = bool(invalid_values)
        if invalid_values:
            results.append(
                ValidationResult(
                    "model_metrics",
                    "fail",
                    f"{model_name} has non-finite metric value(s): {', '.join(invalid_values)}",
                    {"model": model_name, "metrics": invalid_values},
                )
            )

        negative_error_metrics = [
            metric
            for metric in ["rmse", "mae"]
            if metric not in invalid_values and float(model_metrics[metric]) < 0
        ]
        if negative_error_metrics:
            has_failure = True
            results.append(
                ValidationResult(
                    "model_metrics",
                    "fail",
                    f"{model_name} error metrics must be non-negative: {', '.join(negative_error_metrics)}",
                    {"model": model_name, "metrics": negative_error_metrics},
                )
            )

        if "r2" not in invalid_values:
            r2 = float(model_metrics["r2"])
            if not -1 <= r2 <= 1:
                has_failure = True
                results.append(
                    ValidationResult(
                        "model_metrics",
                        "fail",
                        f"{model_name} r2 must be in [-1, 1].",
                        {"model": model_name, "r2": r2},
                    )
                )

        if not has_failure:
            results.append(
                ValidationResult(
                    "model_metrics",
                    "pass",
                    f"{model_name} has finite R2, RMSE, and MAE metrics in valid ranges.",
                    {"model": model_name},
                )
            )
    if not metrics:
        results.append(ValidationResult("model_metrics", "fail", "No model metrics were provided."))
    return results


def check_categorical_encoding_documented(
    config: TaskConfig,
    data: pd.DataFrame,
    evidence: dict[str, Any],
) -> list[ValidationResult]:
    if "functional_zone" not in config.explanatory_variables:
        return []
    if "functional_zone" not in data:
        return [
            ValidationResult(
                "feature_encoding",
                "fail",
                "functional_zone is configured but missing from data.",
            )
        ]

    encoding = evidence.get("feature_encoding", {}).get("functional_zone")
    if not encoding:
        return [
            ValidationResult(
                "feature_encoding",
                "warn",
                "functional_zone categorical encoding is not documented.",
            )
        ]
    if encoding.get("method") != "one_hot" or not encoding.get("encoded_columns"):
        return [
            ValidationResult(
                "feature_encoding",
                "warn",
                "functional_zone categorical encoding documentation is incomplete.",
                {"encoding": encoding},
            )
        ]
    results = [
        ValidationResult(
            "feature_encoding",
            "pass",
            "functional_zone categorical encoding is documented.",
            {"encoding": encoding},
        )
    ]
    missing_allowed = encoding.get("unrepresented_allowed_categories", [])
    if missing_allowed:
        results.append(
            ValidationResult(
                "feature_encoding",
                "warn",
                "Not all allowed functional_zone categories are represented in this synthetic run; allowed and observed categories are documented.",
                {"unrepresented_allowed_categories": missing_allowed},
            )
        )
    return results


def check_spatial_split_strategy(data: pd.DataFrame, evidence: dict[str, Any]) -> list[ValidationResult]:
    split_metadata = evidence.get("split_metadata", {})
    if {"x", "y"}.issubset(data.columns) and split_metadata.get("split_method") == "random":
        return [
            ValidationResult(
                "spatial_split",
                "warn",
                "Random split is used on spatial grid data; spatial leakage may inflate model performance.",
                {"split_metadata": split_metadata},
            )
        ]
    return []


def check_risk_indicator_model_usage(config: TaskConfig, evidence: dict[str, Any]) -> list[ValidationResult]:
    model_features = set(evidence.get("model_features", []))
    misused = sorted(indicator for indicator in config.risk_indicators if indicator in model_features)
    if not misused:
        return []
    return [
        ValidationResult(
            "variable_roles",
            "warn",
            f"risk_indicator variable(s) are included as model features ({', '.join(misused)}); this may indicate target leakage or conceptual misuse.",
            {"risk_indicators_used_as_features": misused},
        )
    ]


def check_predictor_multicollinearity(
    config: TaskConfig,
    data: pd.DataFrame,
    evidence: dict[str, Any],
    threshold: float = MULTICOLLINEARITY_THRESHOLD,
) -> list[ValidationResult]:
    numeric_predictors = [
        predictor
        for predictor in config.predictors
        if predictor in data and pd.api.types.is_numeric_dtype(data[predictor])
        and data[predictor].nunique(dropna=True) > 1
    ]
    if len(numeric_predictors) < 2:
        return []

    correlation_matrix = data[numeric_predictors].corr(numeric_only=True)
    high_pairs: list[dict[str, Any]] = []
    for left_index, left in enumerate(numeric_predictors):
        for right in numeric_predictors[left_index + 1 :]:
            value = correlation_matrix.loc[left, right]
            if np.isfinite(value) and abs(float(value)) > threshold:
                high_pairs.append({"left": left, "right": right, "correlation": float(value)})

    results: list[ValidationResult] = []
    if high_pairs:
        results.append(
            ValidationResult(
                "model_diagnostics",
                "warn",
                "High predictor correlation detected; multicollinearity may make linear coefficients unstable.",
                {"threshold": threshold, "pairs": high_pairs},
            )
        )

    if "building_height" in numeric_predictors:
        height_warnings: list[str] = []
        lst_correlation = data["building_height"].corr(data[config.target_variable]) if config.target_variable in data else None
        coefficient = evidence.get("linear_regression", {}).get("coefficients", {}).get("building_height")
        if (
            coefficient is not None
            and lst_correlation is not None
            and np.isfinite(lst_correlation)
            and coefficient != 0
            and lst_correlation != 0
            and math.copysign(1, coefficient) != math.copysign(1, float(lst_correlation))
        ):
            height_warnings.append("bivariate LST correlation and conditional linear coefficient have inconsistent signs")

        correlated_with_height = [
            pair
            for pair in high_pairs
            if "building_height" in {pair["left"], pair["right"]}
            and ({pair["left"], pair["right"]} - {"building_height"}).pop()
            in {"floor_area_ratio", "building_density", "ndbi"}
        ]
        if correlated_with_height:
            height_warnings.append("building_height is highly correlated with FAR/building_density/NDBI")

        if height_warnings:
            results.append(
                ValidationResult(
                    "model_diagnostics",
                    "warn",
                    "building_height should not be interpreted as a simple directional driver.",
                    {
                        "reasons": height_warnings,
                        "lst_correlation": None if lst_correlation is None else float(lst_correlation),
                        "linear_coefficient": coefficient,
                    },
                )
            )

    return results
