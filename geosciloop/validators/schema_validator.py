from __future__ import annotations

from geosciloop.core.schema import REQUIRED_FIELDS, TaskConfig
from geosciloop.core.state import ValidationResult


def check_config_schema(config: TaskConfig) -> list[ValidationResult]:
    payload = config.to_dict()
    missing = [field for field in REQUIRED_FIELDS if field not in payload or payload[field] in (None, "")]
    if missing:
        return [
            ValidationResult(
                name="config_schema",
                status="fail",
                message=f"Missing required config fields: {', '.join(missing)}",
                details={"missing": missing},
            )
        ]
    return [
        ValidationResult(
            name="config_schema",
            status="pass",
            message="Config includes required v0.1 fields.",
        )
    ]
