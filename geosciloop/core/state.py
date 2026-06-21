from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    name: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    output_dir: Path
    validation_results: list[ValidationResult]
    metrics: dict[str, Any]
    artifacts: dict[str, str]

    @property
    def hard_failures(self) -> list[ValidationResult]:
        return [result for result in self.validation_results if result.status == "fail"]
