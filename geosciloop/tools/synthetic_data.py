from __future__ import annotations

import numpy as np
import pandas as pd

from geosciloop.core.schema import TaskConfig
from geosciloop.tools.spatial_grid import create_square_grid
from geosciloop.tools.spectral_indices import clip_index


def create_synthetic_uhi_data(config: TaskConfig) -> pd.DataFrame:
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
