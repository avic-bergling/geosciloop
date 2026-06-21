from __future__ import annotations

import numpy as np


def clip_index(values):
    return np.clip(values, -1.0, 1.0)
