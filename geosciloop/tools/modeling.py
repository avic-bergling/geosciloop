from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from pandas.api.types import is_numeric_dtype
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from geosciloop.core.schema import TaskConfig
from geosciloop.tools.synthetic_data import ALLOWED_FUNCTIONAL_ZONES


DEFAULT_TEST_SIZE = 0.25


def _metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def _safe_correlation(left: pd.Series, right: pd.Series) -> float | None:
    if left.nunique(dropna=True) <= 1 or right.nunique(dropna=True) <= 1:
        return None
    value = left.corr(right)
    return None if pd.isna(value) else float(value)


def _category_metadata(series: pd.Series, feature: str) -> dict[str, Any]:
    if feature == "functional_zone":
        allowed_categories = list(ALLOWED_FUNCTIONAL_ZONES)
    else:
        allowed_categories = sorted(str(value) for value in series.dropna().unique())
    observed_counts = series.astype(str).value_counts().to_dict()
    observed_categories = [category for category in allowed_categories if observed_counts.get(category, 0) > 0]
    extra_categories = sorted(category for category in observed_counts if category not in allowed_categories)
    if extra_categories:
        allowed_categories = [*allowed_categories, *extra_categories]
        observed_categories.extend(extra_categories)

    baseline_category = allowed_categories[0] if allowed_categories else None
    encoded_columns = [f"{feature}_{category}" for category in allowed_categories[1:]]
    category_counts = {category: int(observed_counts.get(category, 0)) for category in allowed_categories}
    return {
        "method": "one_hot",
        "drop_first": True,
        "allowed_categories": allowed_categories,
        "observed_categories": observed_categories,
        "category_counts": category_counts,
        "baseline_category": baseline_category,
        "encoded_columns": encoded_columns,
        "unrepresented_allowed_categories": [
            category for category in allowed_categories if category_counts.get(category, 0) == 0
        ],
    }


def _prepare_features(data: pd.DataFrame, features: list[str], categorical_variables: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    feature_frame = data[features].copy()
    categorical_features = [
        feature
        for feature in features
        if feature in categorical_variables or not is_numeric_dtype(feature_frame[feature])
    ]
    if not categorical_features:
        return feature_frame, {}

    encoding = {feature: _category_metadata(feature_frame[feature], feature) for feature in categorical_features}
    encoded_input = feature_frame.copy()
    for feature, metadata in encoding.items():
        encoded_input[feature] = encoded_input[feature].astype(
            CategoricalDtype(categories=metadata["allowed_categories"], ordered=True)
        )
    encoded = pd.get_dummies(encoded_input, columns=categorical_features, drop_first=True, dtype=float)
    encoding = {}
    for feature in categorical_features:
        metadata = _category_metadata(feature_frame[feature], feature)
        metadata["encoded_columns"] = [column for column in encoded.columns if column.startswith(f"{feature}_")]
        encoding[feature] = metadata
    return encoded, encoding


def fit_models(data: pd.DataFrame, config: TaskConfig) -> tuple[dict[str, dict[str, Any]], pd.DataFrame]:
    features = config.predictors
    target = config.target_variable
    x_all, feature_encoding = _prepare_features(data, features, config.categorical_variables)
    x_train, x_test, y_train, y_test = train_test_split(
        x_all,
        data[target],
        test_size=DEFAULT_TEST_SIZE,
        random_state=config.random_seed,
    )

    metrics: dict[str, dict[str, Any]] = {}
    prediction_frame = data[["cell_id", target]].copy()

    if "linear_regression" in config.models:
        model = LinearRegression()
        model.fit(x_train, y_train)
        test_predictions = model.predict(x_test)
        full_predictions = model.predict(x_all)
        metrics["linear_regression"] = _metrics(y_test, test_predictions)
        metrics["linear_regression"]["coefficients"] = {
            feature: float(coefficient) for feature, coefficient in zip(x_all.columns, model.coef_)
        }
        metrics["linear_regression"]["intercept"] = float(model.intercept_)
        prediction_frame["linear_regression_prediction"] = full_predictions

    if "random_forest" in config.models:
        model = RandomForestRegressor(n_estimators=80, random_state=config.random_seed, min_samples_leaf=3)
        model.fit(x_train, y_train)
        test_predictions = model.predict(x_test)
        full_predictions = model.predict(x_all)
        metrics["random_forest"] = _metrics(y_test, test_predictions)
        metrics["random_forest"]["feature_importance"] = {
            feature: float(importance) for feature, importance in zip(x_all.columns, model.feature_importances_)
        }
        prediction_frame["random_forest_prediction"] = full_predictions

    correlations = {}
    for feature in features:
        if is_numeric_dtype(data[feature]):
            correlations[feature] = _safe_correlation(data[feature], data[target])
            continue
        for encoded_column in feature_encoding.get(feature, {}).get("encoded_columns", []):
            correlations[encoded_column] = _safe_correlation(x_all[encoded_column], data[target])
    metrics["correlations"] = correlations
    if feature_encoding:
        metrics["feature_encoding"] = feature_encoding
    metrics["split_metadata"] = {
        "split_method": "random",
        "test_size": DEFAULT_TEST_SIZE,
        "random_seed": config.random_seed,
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "raw_predictors": list(features),
        "model_features": list(x_all.columns),
    }
    return metrics, prediction_frame
