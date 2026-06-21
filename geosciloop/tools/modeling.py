from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from geosciloop.core.schema import TaskConfig


def _metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def fit_models(data: pd.DataFrame, config: TaskConfig) -> tuple[dict[str, dict[str, Any]], pd.DataFrame]:
    features = config.explanatory_variables
    target = config.target_variable
    x_train, x_test, y_train, y_test = train_test_split(
        data[features],
        data[target],
        test_size=0.25,
        random_state=config.random_seed,
    )

    metrics: dict[str, dict[str, Any]] = {}
    prediction_frame = data[["cell_id", target]].copy()

    if "linear_regression" in config.models:
        model = LinearRegression()
        model.fit(x_train, y_train)
        test_predictions = model.predict(x_test)
        full_predictions = model.predict(data[features])
        metrics["linear_regression"] = _metrics(y_test, test_predictions)
        metrics["linear_regression"]["coefficients"] = {
            feature: float(coefficient) for feature, coefficient in zip(features, model.coef_)
        }
        metrics["linear_regression"]["intercept"] = float(model.intercept_)
        prediction_frame["linear_regression_prediction"] = full_predictions

    if "random_forest" in config.models:
        model = RandomForestRegressor(n_estimators=80, random_state=config.random_seed, min_samples_leaf=3)
        model.fit(x_train, y_train)
        test_predictions = model.predict(x_test)
        full_predictions = model.predict(data[features])
        metrics["random_forest"] = _metrics(y_test, test_predictions)
        metrics["random_forest"]["feature_importance"] = {
            feature: float(importance) for feature, importance in zip(features, model.feature_importances_)
        }
        prediction_frame["random_forest_prediction"] = full_predictions

    correlations = {feature: float(data[feature].corr(data[target])) for feature in features}
    metrics["correlations"] = correlations
    return metrics, prediction_frame
