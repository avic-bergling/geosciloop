from __future__ import annotations

from typing import Any

from geosciloop.core.state import ValidationResult


CLAIM_PATTERNS = {
    "ndvi": {"labels": ["ndvi"], "negative": "NDVI negative association"},
    "ndwi": {"labels": ["ndwi"], "negative": "NDWI negative association"},
    "ndbi": {"labels": ["ndbi"], "positive": "NDBI positive association"},
    "building_density": {"labels": ["building_density", "building density"], "positive": "building_density positive association"},
    "population_density": {"labels": ["population_density", "population density"], "positive": "population_density positive association"},
    "road_density": {"labels": ["road_density", "road density"], "positive": "road_density positive association"},
}


def _mentions_any(text: str, labels: list[str]) -> bool:
    return any(label in text for label in labels)


def _claim_direction(text: str) -> str | None:
    if any(term in text for term in ["negative", "negatively", "lower", "reduce", "reduces"]):
        return "negative"
    if any(term in text for term in ["positive", "positively", "higher", "increase", "increases"]):
        return "positive"
    return None


def check_conclusion_support(claims: list[str], evidence: dict[str, Any]) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    coefficients = evidence.get("linear_regression", {}).get("coefficients", {})
    correlations = evidence.get("correlations", {})
    causal_design = bool(evidence.get("causal_design"))

    if not causal_design:
        results.append(
            ValidationResult(
                "conclusion_support",
                "warn",
                "No causal design is recorded; causal language should be avoided.",
                {"causal_design": False},
            )
        )

    for claim in claims:
        lowered = claim.lower()
        if any(term in lowered for term in ["cause", "causes", "causal"]):
            results.append(
                ValidationResult(
                    "conclusion_support",
                    "warn",
                    f"Causal language needs causal design support: {claim}",
                )
            )

        if "lst" not in lowered:
            continue

        direction = _claim_direction(lowered)
        if direction is None:
            continue

        for feature, pattern in CLAIM_PATTERNS.items():
            if not _mentions_any(lowered, pattern["labels"]) or direction not in pattern:
                continue
            coefficient = coefficients.get(feature)
            correlation = correlations.get(feature)
            expected_positive = direction == "positive"
            supported_by_coefficient = coefficient is not None and ((coefficient > 0) if expected_positive else (coefficient < 0))
            supported_by_correlation = correlation is not None and ((correlation > 0) if expected_positive else (correlation < 0))
            if supported_by_coefficient or supported_by_correlation:
                results.append(
                    ValidationResult(
                        "conclusion_support",
                        "pass",
                        f"{feature} {direction} association claim is supported by coefficient or correlation evidence.",
                        {"claim": claim, "coefficient": coefficient, "correlation": correlation},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        "conclusion_support",
                        "fail",
                        f"{feature.upper()} {direction} association claim is not supported by available evidence.",
                        {"claim": claim, "coefficient": coefficient, "correlation": correlation},
                    )
                )

    if not [result for result in results if result.status in {"pass", "fail"}]:
        results.append(ValidationResult("conclusion_support", "pass", "No unsupported report claims detected."))
    return results
