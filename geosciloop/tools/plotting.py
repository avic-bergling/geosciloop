from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def save_figures(data: pd.DataFrame, predictions: pd.DataFrame, metrics: dict[str, Any], figures_dir: Path) -> dict[str, str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str] = {}

    plt.figure(figsize=(7, 4))
    plt.hist(data["lst_celsius"], bins=24, color="#4575b4", edgecolor="white")
    plt.xlabel("Synthetic LST (C)")
    plt.ylabel("Cell count")
    plt.title("Synthetic LST distribution")
    path = figures_dir / "lst_distribution.png"
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    artifacts["lst_distribution"] = str(path)

    plt.figure(figsize=(6, 4))
    plt.scatter(data["ndvi"], data["lst_celsius"], s=16, alpha=0.7, color="#1b7837")
    plt.xlabel("NDVI")
    plt.ylabel("Synthetic LST (C)")
    plt.title("NDVI vs synthetic LST")
    path = figures_dir / "ndvi_vs_lst.png"
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    artifacts["ndvi_vs_lst"] = str(path)

    prediction_column = "random_forest_prediction" if "random_forest_prediction" in predictions else "linear_regression_prediction"
    plt.figure(figsize=(5, 5))
    plt.scatter(predictions["lst_celsius"], predictions[prediction_column], s=16, alpha=0.7, color="#762a83")
    low = min(predictions["lst_celsius"].min(), predictions[prediction_column].min())
    high = max(predictions["lst_celsius"].max(), predictions[prediction_column].max())
    plt.plot([low, high], [low, high], color="black", linewidth=1)
    plt.xlabel("Observed synthetic LST (C)")
    plt.ylabel("Predicted synthetic LST (C)")
    plt.title("Predicted vs observed")
    path = figures_dir / "predicted_vs_observed.png"
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    artifacts["predicted_vs_observed"] = str(path)

    importance = metrics.get("random_forest", {}).get("feature_importance", {})
    if importance:
        items = sorted(importance.items(), key=lambda item: item[1])
        plt.figure(figsize=(7, 4))
        plt.barh([item[0] for item in items], [item[1] for item in items], color="#d73027")
        plt.xlabel("Feature importance")
        plt.title("Random forest feature importance")
        path = figures_dir / "feature_importance.png"
        plt.tight_layout()
        plt.savefig(path, dpi=140)
        plt.close()
        artifacts["feature_importance"] = str(path)

    return artifacts
