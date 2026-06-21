from __future__ import annotations

import numpy as np
import pandas as pd

from geosciloop.core.schema import TaskConfig
from geosciloop.tools.spatial_grid import create_square_grid
from geosciloop.tools.spectral_indices import clip_index


ALLOWED_FUNCTIONAL_ZONES = ("residential", "commercial", "industrial", "mixed_use", "park", "water")
MORPHOLOGY_COLUMNS = {"building_height", "floor_area_ratio", "functional_zone", "population_exposure"}


def _uses_morphology_demo(config: TaskConfig) -> bool:
    return bool(MORPHOLOGY_COLUMNS.intersection(config.explanatory_variables))


def create_synthetic_uhi_data(config: TaskConfig) -> pd.DataFrame:
    if _uses_morphology_demo(config):
        return create_synthetic_morphology_uhi_data(config)

    rng = np.random.default_rng(config.random_seed)
    data = create_square_grid(config.n_cells, config.grid_size_m)

    center_strength = 1.0 - data["distance_to_center_norm"].to_numpy()
    built_intensity = np.clip(0.15 + 0.75 * center_strength + rng.normal(0, 0.08, config.n_cells), 0, 1)
    water_presence = np.clip(0.18 * (1 - center_strength) + rng.normal(0, 0.04, config.n_cells), 0, 0.55)

    data["ndvi"] = clip_index(0.62 - 0.72 * built_intensity - 0.18 * water_presence + rng.normal(0, 0.08, config.n_cells))
    data["ndbi"] = clip_index(-0.22 + 0.95 * built_intensity + rng.normal(0, 0.07, config.n_cells))
    data["ndwi"] = clip_index(-0.10 + 0.85 * water_presence - 0.18 * built_intensity + rng.normal(0, 0.05, config.n_cells))
    data["population_density"] = np.maximum(0, 900 + 7600 * built_intensity + rng.normal(0, 450, config.n_cells))
    data["road_density"] = np.maximum(0, 0.8 + 8.5 * built_intensity + rng.normal(0, 0.5, config.n_cells))
    data["building_density"] = np.maximum(0, 0.05 + 0.9 * built_intensity + rng.normal(0, 0.06, config.n_cells))

    population_norm = data["population_density"] / max(float(data["population_density"].max()), 1.0)
    road_norm = data["road_density"] / max(float(data["road_density"].max()), 1.0)
    data["lst_celsius"] = (
        31.0
        - 5.8 * data["ndvi"]
        - 2.1 * data["ndwi"]
        + 4.5 * data["ndbi"]
        + 3.8 * data["building_density"]
        + 1.6 * population_norm
        + 1.2 * road_norm
        + rng.normal(0, 0.9, config.n_cells)
    )
    data["lst_celsius"] = data["lst_celsius"].clip(-30, 80)
    return data.drop(columns=["distance_to_center_norm"])


def build_synthetic_truth(config: TaskConfig) -> dict[str, object]:
    if _uses_morphology_demo(config):
        return {
            "generator": "create_synthetic_morphology_uhi_data",
            "random_seed": config.random_seed,
            "formula_description": (
                "Synthetic LST is generated from NDVI, NDWI, NDBI, building_density, "
                "floor_area_ratio, road density, mixed building-height terms, and functional-zone adjustments, "
                "plus Gaussian noise. population_exposure is derived after population_density and heat relevance "
                "and is intended for exposure interpretation rather than default LST prediction."
            ),
            "pseudocode": [
                "built_intensity <- center_strength + corridor_strength + noise",
                "functional_zone <- rules over built_intensity, center_strength, corridor_strength, vegetation, water",
                "building_height <- zone base height + center morphology term + noise",
                "floor_area_ratio <- building_density * building_height + center term + noise",
                "population_exposure <- population_density * heat_relevance",
                "lst_celsius <- negative NDVI/NDWI + positive NDBI/building_density/FAR/road + mixed height terms + zone adjustment + noise",
            ],
            "true_coefficient_signs": {
                "ndvi": "negative",
                "ndwi": "negative",
                "ndbi": "positive",
                "building_density": "positive",
                "floor_area_ratio": "positive",
                "road_density": "positive",
                "building_height": "mixed",
                "functional_zone": "category_adjustment",
                "population_density": "indirect_via_exposure_context",
                "population_exposure": "risk_indicator",
            },
            "noise": {"distribution": "normal", "lst_celsius_sd": 0.85},
            "intended_predictors": list(config.predictors),
            "risk_indicators": list(config.risk_indicators),
            "notes": [
                "All outputs are synthetic and are not evidence about a real city.",
                "population_exposure is not a default LST predictor.",
                "building_height is intentionally mixed and should not be interpreted as a simple directional driver.",
            ],
        }

    return {
        "generator": "create_synthetic_uhi_data",
        "random_seed": config.random_seed,
        "formula_description": (
            "Synthetic LST is generated from negative NDVI/NDWI terms, positive NDBI/building_density terms, "
            "normalized population and road density terms, plus Gaussian noise."
        ),
        "pseudocode": [
            "built_intensity <- center_strength + noise",
            "water_presence <- edge-weighted water signal + noise",
            "lst_celsius <- negative NDVI/NDWI + positive NDBI/building_density/population/road terms + noise",
        ],
        "true_coefficient_signs": {
            "ndvi": "negative",
            "ndwi": "negative",
            "ndbi": "positive",
            "building_density": "positive",
            "population_density": "positive",
            "road_density": "positive",
        },
        "noise": {"distribution": "normal", "lst_celsius_sd": 0.9},
        "intended_predictors": list(config.predictors),
        "risk_indicators": list(config.risk_indicators),
        "notes": ["All outputs are synthetic and are not evidence about a real city."],
    }


def create_synthetic_morphology_uhi_data(config: TaskConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed)
    data = create_square_grid(config.n_cells, config.grid_size_m)

    center_strength = 1.0 - data["distance_to_center_norm"].to_numpy()
    x_norm = (data["x"].to_numpy() - data["x"].min()) / max(float(data["x"].max() - data["x"].min()), 1.0)
    y_norm = (data["y"].to_numpy() - data["y"].min()) / max(float(data["y"].max() - data["y"].min()), 1.0)
    corridor_strength = np.exp(-((x_norm - 0.52) ** 2) / 0.012) + np.exp(-((y_norm - 0.48) ** 2) / 0.018)
    corridor_strength = np.clip(corridor_strength / corridor_strength.max(), 0, 1)

    built_intensity = np.clip(
        0.12 + 0.68 * center_strength + 0.20 * corridor_strength + rng.normal(0, 0.07, config.n_cells),
        0,
        1,
    )
    water_presence = np.clip(
        0.32 * (1 - center_strength) * (1 - corridor_strength) + rng.normal(0, 0.05, config.n_cells),
        0,
        0.75,
    )
    vegetation_signal = np.clip(
        0.70 - 0.62 * built_intensity + 0.16 * (1 - center_strength) - 0.14 * water_presence
        + rng.normal(0, 0.08, config.n_cells),
        0,
        1,
    )

    zones = np.full(config.n_cells, "residential", dtype=object)
    zones[(built_intensity > 0.70) & (center_strength > 0.62)] = "commercial"
    zones[(built_intensity > 0.62) & (corridor_strength > 0.55) & (center_strength <= 0.70)] = "industrial"
    zones[(built_intensity > 0.42) & (built_intensity <= 0.76) & (center_strength > 0.35)] = "mixed_use"
    zones[(vegetation_signal > 0.58) & (built_intensity < 0.44)] = "park"
    zones[water_presence > 0.43] = "water"

    zone_height_base = {
        "residential": 11.0,
        "commercial": 36.0,
        "industrial": 15.0,
        "mixed_use": 22.0,
        "park": 1.5,
        "water": 0.2,
    }
    height_base = np.array([zone_height_base[zone] for zone in zones], dtype=float)
    data["building_height"] = np.maximum(
        0,
        height_base + 18.0 * center_strength * built_intensity + rng.normal(0, 4.0, config.n_cells),
    )
    data.loc[np.isin(zones, ["park", "water"]), "building_height"] = np.maximum(
        0,
        data.loc[np.isin(zones, ["park", "water"]), "building_height"].to_numpy() * 0.25,
    )

    data["building_density"] = np.maximum(
        0,
        np.clip(0.04 + 0.88 * built_intensity - 0.30 * water_presence + rng.normal(0, 0.05, config.n_cells), 0, 1),
    )
    data["floor_area_ratio"] = np.maximum(
        0,
        np.clip(
            0.20 + data["building_density"] * data["building_height"] / 10.0 + 0.40 * center_strength
            + rng.normal(0, 0.25, config.n_cells),
            0,
            8.5,
        ),
    )

    zone_population_factor = {
        "residential": 1.0,
        "commercial": 0.75,
        "industrial": 0.32,
        "mixed_use": 1.18,
        "park": 0.08,
        "water": 0.02,
    }
    population_factor = np.array([zone_population_factor[zone] for zone in zones], dtype=float)
    data["population_density"] = np.maximum(
        0,
        population_factor * (750 + 8900 * built_intensity + 950 * center_strength)
        + rng.normal(0, 430, config.n_cells),
    )
    data["road_density"] = np.maximum(
        0,
        0.45 + 7.9 * built_intensity + 2.0 * corridor_strength + rng.normal(0, 0.45, config.n_cells),
    )

    data["ndvi"] = clip_index(
        0.58 + 0.34 * vegetation_signal - 0.66 * built_intensity - 0.16 * water_presence
        + rng.normal(0, 0.06, config.n_cells)
    )
    data["ndbi"] = clip_index(-0.28 + 0.96 * built_intensity + 0.10 * data["floor_area_ratio"] / 8.5 + rng.normal(0, 0.06, config.n_cells))
    data["ndwi"] = clip_index(-0.18 + 0.92 * water_presence - 0.16 * built_intensity + rng.normal(0, 0.05, config.n_cells))

    heat_relevance = np.clip(0.38 + 0.42 * built_intensity + 0.20 * (1 - vegetation_signal), 0, 1.2)
    data["population_exposure"] = np.maximum(0, data["population_density"] * heat_relevance)

    road_norm = data["road_density"] / max(float(data["road_density"].max()), 1.0)
    height_shade_term = -0.030 * np.minimum(data["building_height"], 25.0)
    height_canyon_term = 0.010 * np.maximum(data["building_height"] - 25.0, 0.0)
    zone_lst_adjustment = pd.Series(zones).map(
        {
            "residential": 0.25,
            "commercial": 0.55,
            "industrial": 0.95,
            "mixed_use": 0.35,
            "park": -0.55,
            "water": -1.10,
        }
    ).to_numpy(dtype=float)

    data["functional_zone"] = zones
    data["lst_celsius"] = (
        31.2
        - 5.4 * data["ndvi"]
        - 2.4 * data["ndwi"]
        + 4.0 * data["ndbi"]
        + 2.6 * data["building_density"]
        + 0.48 * data["floor_area_ratio"]
        + 0.75 * road_norm
        + height_shade_term
        + height_canyon_term
        + zone_lst_adjustment
        + rng.normal(0, 0.85, config.n_cells)
    )
    data["lst_celsius"] = data["lst_celsius"].clip(-30, 80)
    return data.drop(columns=["distance_to_center_norm"])
