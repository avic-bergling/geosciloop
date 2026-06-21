import math

import pandas as pd

from geosciloop.core.schema import load_task_config
from geosciloop.validators.conclusion_support import check_conclusion_support
from geosciloop.validators.value_ranges import check_missing_values, check_value_ranges
from geosciloop.validators.model_diagnostics import check_model_metrics_exist
from geosciloop.validators.validator_suite import run_validator_suite


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


def test_value_range_validator_checks_morphology_fields_and_functional_zone():
    data = pd.DataFrame(
        {
            "ndvi": [0.2, 0.3],
            "ndwi": [0.1, 0.0],
            "ndbi": [0.3, 0.4],
            "lst_celsius": [35.0, 36.0],
            "population_density": [10.0, 11.0],
            "road_density": [2.0, 3.0],
            "building_density": [0.5, 0.7],
            "building_height": [12.0, -1.0],
            "floor_area_ratio": [1.5, -0.2],
            "population_exposure": [400.0, -5.0],
            "functional_zone": ["residential", "airport"],
        }
    )

    results = check_value_ranges(data)

    assert any(result.status == "fail" and "building_height" in result.message for result in results)
    assert any(result.status == "fail" and "floor_area_ratio" in result.message for result in results)
    assert any(result.status == "fail" and "population_exposure" in result.message for result in results)
    assert any(result.status == "fail" and "functional_zone" in result.message for result in results)


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


def test_conclusion_support_warns_on_oversimplified_building_height_claim():
    results = check_conclusion_support(
        claims=["building_height is positively associated with LST."],
        evidence={
            "linear_regression": {"coefficients": {"building_height": 0.5}},
            "correlations": {"building_height": 0.2},
        },
    )

    assert any(
        result.status == "warn"
        and "building_height" in result.message
        and "oversimplified" in result.message.lower()
        for result in results
    )


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


def test_validator_suite_warns_when_functional_zone_encoding_is_not_documented():
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)
    data = pd.DataFrame(
        {
            "ndvi": [0.2, 0.3],
            "ndwi": [0.1, 0.0],
            "ndbi": [0.3, 0.4],
            "lst_celsius": [35.0, 36.0],
            "population_density": [10.0, 11.0],
            "road_density": [2.0, 3.0],
            "building_density": [0.5, 0.7],
            "building_height": [12.0, 9.0],
            "floor_area_ratio": [1.5, 1.2],
            "population_exposure": [400.0, 500.0],
            "functional_zone": ["residential", "commercial"],
        }
    )
    metrics = {
        "linear_regression": {"r2": 0.5, "rmse": 1.0, "mae": 0.8},
        "random_forest": {"r2": 0.6, "rmse": 0.9, "mae": 0.7},
    }

    results = run_validator_suite(config, data, metrics, claims=[], evidence={})

    assert any(
        result.status == "warn"
        and "functional_zone" in result.message
        and "encoding" in result.message.lower()
        for result in results
    )


def test_validator_suite_warns_on_random_split_for_spatial_grid_data():
    config = load_task_config("configs/uhi_synthetic_demo.yaml", offline_override=True)
    data = pd.DataFrame(
        {
            "cell_id": [0, 1, 2, 3],
            "x": [0.0, 1.0, 0.0, 1.0],
            "y": [0.0, 0.0, 1.0, 1.0],
            "ndvi": [0.2, 0.3, 0.4, 0.5],
            "ndwi": [0.0, 0.1, 0.0, 0.1],
            "ndbi": [0.3, 0.4, 0.5, 0.6],
            "lst_celsius": [35.0, 36.0, 37.0, 38.0],
            "population_density": [10.0, 11.0, 12.0, 13.0],
            "road_density": [2.0, 3.0, 4.0, 5.0],
            "building_density": [0.5, 0.6, 0.7, 0.8],
        }
    )
    metrics = {"linear_regression": {"r2": 0.5, "rmse": 1.0, "mae": 0.8}}

    results = run_validator_suite(
        config,
        data,
        metrics,
        claims=[],
        evidence={"split_metadata": {"split_method": "random"}},
    )

    assert any(
        result.status == "warn"
        and result.message == "Random split is used on spatial grid data; spatial leakage may inflate model performance."
        for result in results
    )


def test_validator_suite_warns_on_highly_correlated_numeric_predictors():
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)
    data = pd.DataFrame(
        {
            "cell_id": [0, 1, 2, 3, 4],
            "x": [0, 1, 2, 3, 4],
            "y": [0, 0, 0, 0, 0],
            "ndvi": [0.5, 0.4, 0.3, 0.2, 0.1],
            "ndwi": [0.2, 0.1, 0.0, -0.1, -0.2],
            "ndbi": [0.1, 0.2, 0.3, 0.4, 0.5],
            "building_density": [0.1, 0.2, 0.3, 0.4, 0.5],
            "building_height": [2.0, 4.0, 6.0, 8.0, 10.0],
            "floor_area_ratio": [0.2, 0.4, 0.6, 0.8, 1.0],
            "population_density": [100, 200, 300, 400, 500],
            "population_exposure": [50, 100, 150, 200, 250],
            "road_density": [1, 2, 3, 4, 5],
            "functional_zone": ["residential", "residential", "commercial", "commercial", "park"],
            "lst_celsius": [32.0, 33.0, 34.0, 35.0, 36.0],
        }
    )
    metrics = {"linear_regression": {"r2": 0.5, "rmse": 1.0, "mae": 0.8}}

    results = run_validator_suite(
        config,
        data,
        metrics,
        claims=[],
        evidence={
            "model_features": config.predictors,
            "linear_regression": {"coefficients": {"building_height": -0.4}},
            "correlations": {"building_height": 0.99},
        },
    )

    assert any(result.status == "warn" and "High predictor correlation" in result.message for result in results)
    assert any(result.status == "warn" and "building_height" in result.message for result in results)


def test_validator_suite_warns_if_risk_indicator_is_used_as_model_feature():
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)
    data = pd.DataFrame(
        {
            "cell_id": [0, 1],
            "x": [0.0, 1.0],
            "y": [0.0, 1.0],
            "ndvi": [0.2, 0.3],
            "ndwi": [0.1, 0.0],
            "ndbi": [0.3, 0.4],
            "lst_celsius": [35.0, 36.0],
            "population_density": [10.0, 11.0],
            "road_density": [2.0, 3.0],
            "building_density": [0.5, 0.7],
            "building_height": [12.0, 9.0],
            "floor_area_ratio": [1.5, 1.2],
            "population_exposure": [400.0, 500.0],
            "functional_zone": ["residential", "commercial"],
        }
    )
    metrics = {"linear_regression": {"r2": 0.5, "rmse": 1.0, "mae": 0.8}}

    results = run_validator_suite(
        config,
        data,
        metrics,
        claims=[],
        evidence={"model_features": [*config.predictors, "population_exposure"]},
    )

    assert any(
        result.status == "warn"
        and "population_exposure" in result.message
        and "risk_indicator" in result.message
        for result in results
    )
