from __future__ import annotations

from typing import Any

import pandas as pd

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import ValidationResult
from geosciloop.validators.conclusion_support import check_conclusion_support
from geosciloop.validators.model_diagnostics import check_model_metrics_exist
from geosciloop.validators.schema_validator import check_config_schema
from geosciloop.validators.value_ranges import check_missing_values, check_value_ranges


def run_validator_suite(
    config: TaskConfig,
    data: pd.DataFrame,
    model_metrics: dict[str, dict[str, Any]],
    claims: list[str],
    evidence: dict[str, Any],
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    results.extend(check_config_schema(config))
    results.extend(check_value_ranges(data))
    results.extend(check_missing_values(data))
    results.extend(check_model_metrics_exist(model_metrics))
    results.extend(check_conclusion_support(claims, evidence))
    return results
