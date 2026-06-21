from __future__ import annotations

import math

import numpy as np
import pandas as pd


def create_square_grid(n_cells: int, grid_size_m: int) -> pd.DataFrame:
    side = math.ceil(math.sqrt(n_cells))
    coords = []
    for index in range(n_cells):
        row = index // side
        col = index % side
        coords.append(
            {
                "cell_id": f"cell_{index:04d}",
                "x": col * grid_size_m,
                "y": row * grid_size_m,
            }
        )
    grid = pd.DataFrame(coords)
    center_x = (side - 1) * grid_size_m / 2
    center_y = (side - 1) * grid_size_m / 2
    distance = np.sqrt((grid["x"] - center_x) ** 2 + (grid["y"] - center_y) ** 2)
    max_distance = float(distance.max()) if distance.max() else 1.0
    grid["distance_to_center_norm"] = distance / max_distance
    return grid
