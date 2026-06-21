from __future__ import annotations

from typing import Any

from geosciloop.core.state import ValidationResult


def summarize_warnings(validation_results: list[ValidationResult], metrics: dict[str, Any]) -> dict[str, Any]:
    warnings = [result.message for result in validation_results if result.status == "warn"]
    failures = [result.message for result in validation_results if result.status == "fail"]
    limitations = [
        "This is a deterministic synthetic demo, not a real remote-sensing product.",
        "The model uses a random train/test split; future real-data workflows should consider spatial leakage.",
        "Observed associations should not be interpreted as causal effects.",
        "LST is not the same as air temperature.",
    ]
    if metrics.get("models", {}).get("linear_regression", {}).get("r2", 1.0) < 0.3:
        limitations.append("Linear model fit is weak for this run.")
    return {"warnings": warnings, "failures": failures, "limitations": limitations}
