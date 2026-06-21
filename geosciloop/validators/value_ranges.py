from __future__ import annotations

import numpy as np
import pandas as pd

from geosciloop.core.state import ValidationResult
from geosciloop.tools.synthetic_data import ALLOWED_FUNCTIONAL_ZONES


INDEX_COLUMNS = ["ndvi", "ndwi", "ndbi"]
DENSITY_COLUMNS = {
    "population_density": 100000.0,
    "road_density": 100.0,
    "building_density": 1.0,
}
OPTIONAL_NON_NEGATIVE_COLUMNS = {
    "building_height": 200.0,
    "floor_area_ratio": 25.0,
    "population_exposure": 500000.0,
}


def _numeric_series(data: pd.DataFrame, column: str) -> tuple[pd.Series | None, list[ValidationResult]]:
    if column not in data:
        return None, [ValidationResult("value_ranges", "fail", f"Missing column: {column}")]

    raw = data[column]
    numeric = pd.to_numeric(raw, errors="coerce")
    non_numeric_mask = numeric.isna() & raw.notna()
    results: list[ValidationResult] = []
    if non_numeric_mask.any():
        results.append(
            ValidationResult(
                "value_ranges",
                "fail",
                f"{column} contains non-numeric values.",
                {"count": int(non_numeric_mask.sum())},
            )
        )

    finite_mask = np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan))
    non_finite_mask = raw.notna() & ~non_numeric_mask & ~finite_mask
    if non_finite_mask.any():
        results.append(
            ValidationResult(
                "value_ranges",
                "fail",
                f"{column} contains non-finite values.",
                {"count": int(non_finite_mask.sum())},
            )
        )

    return numeric, results


def check_value_ranges(data: pd.DataFrame) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    for column in INDEX_COLUMNS:
        numeric, column_results = _numeric_series(data, column)
        results.extend(column_results)
        if numeric is None:
            continue
        finite = numeric[numeric.notna() & np.isfinite(numeric)]
        invalid = finite[~finite.between(-1, 1)]
        if invalid.empty:
            results.append(ValidationResult("value_ranges", "pass", f"{column} is within [-1, 1]."))
        else:
            results.append(
                ValidationResult(
                    "value_ranges",
                    "fail",
                    f"{column} has values outside [-1, 1].",
                    {"count": int(len(invalid))},
                )
            )

    if "lst_celsius" not in data:
        results.append(ValidationResult("value_ranges", "fail", "Missing LST column: lst_celsius"))
    else:
        numeric, column_results = _numeric_series(data, "lst_celsius")
        results.extend(column_results)
        if numeric is not None:
            finite = numeric[numeric.notna() & np.isfinite(numeric)]
            invalid_lst = finite[~finite.between(-30, 80)]
            status = "pass" if invalid_lst.empty else "fail"
            message = "lst_celsius is within [-30, 80]." if invalid_lst.empty else "lst_celsius has implausible values."
            results.append(ValidationResult("value_ranges", status, message, {"count": int(len(invalid_lst))}))

    for column, upper_bound in DENSITY_COLUMNS.items():
        numeric, column_results = _numeric_series(data, column)
        results.extend(column_results)
        if numeric is None:
            continue
        finite = numeric[numeric.notna() & np.isfinite(numeric)]
        invalid = finite[finite < 0]
        status = "pass" if invalid.empty else "fail"
        message = f"{column} is non-negative." if invalid.empty else f"{column} has negative values."
        results.append(ValidationResult("value_ranges", status, message, {"count": int(len(invalid))}))
        high = finite[finite > upper_bound]
        if not high.empty:
            results.append(
                ValidationResult(
                    "value_ranges",
                    "warn",
                    f"{column} has values above the v0.1 plausible synthetic threshold.",
                    {"count": int(len(high)), "threshold": upper_bound},
                )
            )

    for column, upper_bound in OPTIONAL_NON_NEGATIVE_COLUMNS.items():
        if column not in data:
            continue
        numeric, column_results = _numeric_series(data, column)
        results.extend(column_results)
        if numeric is None:
            continue
        finite = numeric[numeric.notna() & np.isfinite(numeric)]
        invalid = finite[finite < 0]
        status = "pass" if invalid.empty else "fail"
        message = f"{column} is non-negative." if invalid.empty else f"{column} has negative values."
        results.append(ValidationResult("value_ranges", status, message, {"count": int(len(invalid))}))
        high = finite[finite > upper_bound]
        if not high.empty:
            results.append(
                ValidationResult(
                    "value_ranges",
                    "warn",
                    f"{column} has values above the v0.1 plausible synthetic threshold.",
                    {"count": int(len(high)), "threshold": upper_bound},
                )
            )

    if "functional_zone" in data:
        allowed = set(ALLOWED_FUNCTIONAL_ZONES)
        invalid_zone = data.loc[~data["functional_zone"].isin(allowed), "functional_zone"]
        if invalid_zone.empty:
            results.append(
                ValidationResult(
                    "value_ranges",
                    "pass",
                    "functional_zone values are within the allowed set.",
                    {"allowed_values": sorted(allowed)},
                )
            )
        else:
            results.append(
                ValidationResult(
                    "value_ranges",
                    "fail",
                    "functional_zone has values outside the allowed set.",
                    {"invalid_values": sorted(str(value) for value in invalid_zone.unique())},
                )
            )

    return results


def check_missing_values(data: pd.DataFrame) -> list[ValidationResult]:
    missing = data.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        return [ValidationResult("missing_values", "pass", "No missing values detected.")]
    return [
        ValidationResult(
            "missing_values",
            "fail",
            "Missing values detected.",
            {"columns": {column: int(count) for column, count in missing.items()}},
        )
    ]
