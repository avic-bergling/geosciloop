from __future__ import annotations

from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_text
from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import ValidationResult
from geosciloop.report.markdown_writer import build_report_markdown


def write_report(
    config: TaskConfig,
    plan: dict[str, Any],
    metrics: dict[str, Any],
    validation_results: list[ValidationResult],
    critic_summary: dict[str, Any],
    path: Path,
) -> tuple[str, list[dict[str, Any]]]:
    report, claims = build_report_markdown(config, plan, metrics, validation_results, critic_summary)
    write_text(path, report)
    return report, claims
