import math

import pandas as pd

from geosciloop.validators.conclusion_support import check_conclusion_support
from geosciloop.validators.value_ranges import check_missing_values, check_value_ranges
from geosciloop.validators.model_diagnostics import check_model_metrics_exist


def test_value_range_validator_flags_invalid_indices_and_density():
    data = pd.DataFrame(
        {
            "ndvi": [0.2, 1.2],
            "ndwi": [0.1, 0.0],
            "ndbi": [0.3, -0.2],
            "lst_celsius": [35.0, 36.0],
            "population_density": [10.0, -1.0],
            "road_density": [2.0, 3.0],
            "building_density": [0.5, 0.7],
        }
    )

    results = check_value_ranges(data)

    assert any(result.status == "fail" and "ndvi" in result.message for result in results)
    assert any(result.status == "fail" and "population_density" in result.message for result in results)


def test_value_range_validator_flags_non_numeric_and_infinite_values():
    data = pd.DataFrame(
        {
            "ndvi": [0.2, "bad"],
            "ndwi": [0.1, math.inf],
            "ndbi": [0.3, -0.2],
            "lst_celsius": [35.0, 36.0],
            "population_density": [10.0, 11.0],
            "road_density": [2.0, 3.0],
            "building_density": [0.5, 0.7],
        }
    )

    results = check_value_ranges(data)

    assert any(result.status == "fail" and "ndvi" in result.message and "non-numeric" in result.message for result in results)
    assert any(result.status == "fail" and "ndwi" in result.message and "non-finite" in result.message for result in results)


def test_value_range_validator_warns_on_implausibly_high_density_values():
    data = pd.DataFrame(
        {
            "ndvi": [0.2],
            "ndwi": [0.1],
            "ndbi": [0.3],
            "lst_celsius": [35.0],
            "population_density": [150000.0],
            "road_density": [150.0],
            "building_density": [2.0],
        }
    )

    results = check_value_ranges(data)

    assert any(result.status == "warn" and "population_density" in result.message for result in results)
    assert any(result.status == "warn" and "road_density" in result.message for result in results)
    assert any(result.status == "warn" and "building_density" in result.message for result in results)


def test_missing_value_validator_flags_nulls():
    data = pd.DataFrame({"ndvi": [0.2, None], "lst_celsius": [35.0, 36.0]})

    results = check_missing_values(data)

    assert any(result.status == "fail" and "missing" in result.message.lower() for result in results)
    assert results[0].details["columns"] == {"ndvi": 1}


def test_model_metrics_validator_requires_core_metrics():
    results = check_model_metrics_exist({"linear_regression": {"r2": 0.5}})

    assert any(result.status == "fail" and "rmse" in result.message.lower() for result in results)


def test_model_metrics_validator_rejects_non_finite_and_invalid_metric_values():
    results = check_model_metrics_exist(
        {
            "linear_regression": {"r2": float("nan"), "rmse": -1.0, "mae": float("inf")},
            "random_forest": {"r2": 1.2, "rmse": 0.5, "mae": 0.2},
        }
    )

    assert any(result.status == "fail" and "finite" in result.message.lower() for result in results)
    assert any(result.status == "fail" and "non-negative" in result.message.lower() for result in results)
    assert any(result.status == "fail" and "r2" in result.message.lower() and "[-1, 1]" in result.message for result in results)


def test_conclusion_support_warns_on_causal_claim():
    results = check_conclusion_support(
        claims=["NDVI causes lower LST."],
        evidence={"linear_regression": {"coefficients": {"ndvi": -2.0}}},
    )

    assert any(result.status == "warn" and "causal" in result.message.lower() for result in results)


def test_conclusion_support_fails_unsupported_positive_built_claim():
    results = check_conclusion_support(
        claims=["NDBI is positively associated with LST."],
        evidence={"linear_regression": {"coefficients": {"ndbi": -0.5}}, "correlations": {"ndbi": -0.2}},
    )

    assert any(result.status == "fail" and "NDBI" in result.message for result in results)


def test_conclusion_support_passes_supported_positive_building_density_claim():
    results = check_conclusion_support(
        claims=["building_density is positively associated with LST."],
        evidence={
            "linear_regression": {"coefficients": {"building_density": 3.0}},
            "correlations": {"building_density": 0.7},
        },
    )

    assert any(result.status == "pass" and "building_density" in result.message for result in results)
