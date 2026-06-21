from __future__ import annotations

from pathlib import Path
from typing import Any

from geosciloop.core.state import ValidationResult


def evaluate_run(output_dir: Path, metrics: dict[str, Any], validation_results: list[ValidationResult]) -> dict[str, Any]:
    required_artifacts = [
        "data_manifest.json",
        "research_plan.yaml",
        "research_ledger.json",
        "validation_report.json",
        "metrics.json",
        "report.md",
        "run_log.json",
    ]
    artifact_status = {artifact: (output_dir / artifact).exists() for artifact in required_artifacts}
    validator_counts = {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }
    return {
        "execution_success": all(artifact_status.values()) and validator_counts["fail"] == 0,
        "artifact_completeness": artifact_status,
        "data_validity": validator_counts["fail"] == 0,
        "model_metric_availability": all(
            metric in model_metrics
            for model_metrics in metrics.get("models", {}).values()
            for metric in ["r2", "rmse", "mae"]
        ),
        "validator_counts": validator_counts,
        "report_claim_support": validator_counts["fail"] == 0,
        "reproducibility": "fixed random_seed and offline synthetic data",
    }
