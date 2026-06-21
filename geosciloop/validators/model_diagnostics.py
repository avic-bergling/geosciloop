from __future__ import annotations

import math
from typing import Any

from geosciloop.core.state import ValidationResult


REQUIRED_METRICS = ["r2", "rmse", "mae"]


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
