from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_json
from geosciloop.core.state import ValidationResult


SCHEMA_VERSION = "geosciloop-benchmark-v0.1"
EVALUATION_MODE = "offline_v0_1"
REQUIRED_MODEL_METRICS = ("r2", "rmse", "mae")
REQUIRED_REPRODUCIBILITY_FIELDS = (
    "data_manifest.random_seed",
    "data_manifest.offline",
    "synthetic_truth.random_seed",
    "metrics.variable_roles",
    "metrics.split_metadata",
    "run_log.split_metadata",
    "research_ledger.variable_roles",
    "research_ledger.synthetic_truth",
    "research_ledger.split_metadata",
)
REQUIRED_ARTIFACTS = {
    "data_manifest.json": "file",
    "research_plan.yaml": "file",
    "research_ledger.json": "file",
    "validation_report.json": "file",
    "metrics.json": "file",
    "report.md": "file",
    "summary.md": "file",
    "synthetic_truth.json": "file",
    "run_log.json": "file",
    "figures/": "dir",
    "tables/": "dir",
    "tables/synthetic_uhi_data.csv": "file",
    "tables/model_predictions.csv": "file",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _status(score: float, *, warn_when_partial: bool = False) -> str:
    if score >= 1.0:
        return "pass"
    if warn_when_partial and score > 0:
        return "warn"
    return "fail"


def _sub_score(score: float, details: dict[str, Any], *, warn_when_partial: bool = False) -> dict[str, Any]:
    rounded = round(float(score), 3)
    return {
        "score": rounded,
        "status": _status(rounded, warn_when_partial=warn_when_partial),
        "details": details,
    }


def _artifact_status(output_dir: Path) -> dict[str, bool]:
    return {
        artifact: (output_dir / artifact).is_dir() if artifact_type == "dir" else (output_dir / artifact).is_file()
        for artifact, artifact_type in REQUIRED_ARTIFACTS.items()
    }


def _validator_counts(validation_results: list[ValidationResult]) -> dict[str, int]:
    return {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }


def _model_metric_availability(metrics: dict[str, Any]) -> dict[str, Any]:
    models = metrics.get("models", {})
    if not models:
        return {"score": 0.0, "models": {}, "missing": ["models"]}

    model_status: dict[str, dict[str, Any]] = {}
    available = 0
    total = 0
    missing: list[str] = []
    invalid: list[str] = []
    for model_name, model_metrics in models.items():
        present = []
        model_missing = []
        model_invalid = []
        for metric_name in REQUIRED_MODEL_METRICS:
            total += 1
            value = model_metrics.get(metric_name)
            if metric_name not in model_metrics:
                model_missing.append(metric_name)
                missing.append(f"{model_name}.{metric_name}")
                continue
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                model_invalid.append(metric_name)
                invalid.append(f"{model_name}.{metric_name}")
                continue
            available += 1
            present.append(metric_name)
        model_status[model_name] = {
            "present": present,
            "missing": model_missing,
            "invalid": model_invalid,
        }
    return {
        "score": available / total if total else 0.0,
        "models": model_status,
        "missing": missing,
        "invalid": invalid,
    }


def _report_claim_support(output_dir: Path) -> dict[str, Any]:
    ledger = _read_json(output_dir / "research_ledger.json")
    claims = ledger.get("report_claims", [])
    if not claims:
        return {"score": 0.0, "claims": [], "missing": ["research_ledger.report_claims"]}

    supported = []
    unsupported = []
    for claim in claims:
        is_supported = (
            claim.get("support_status") == "supported"
            and bool(claim.get("supporting_artifacts"))
            and bool(claim.get("evidence"))
        )
        if is_supported:
            supported.append(claim.get("claim", ""))
        else:
            unsupported.append(claim.get("claim", ""))
    return {
        "score": len(supported) / len(claims),
        "claims": {"supported": supported, "unsupported": unsupported, "total": len(claims)},
    }


def _has_nested(payload: dict[str, Any], dotted_path: str) -> bool:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current or current[part] in ({}, [], None, ""):
            return False
        current = current[part]
    return True


def _reproducibility_metadata(output_dir: Path, metrics: dict[str, Any]) -> dict[str, Any]:
    sources = {
        "data_manifest": _read_json(output_dir / "data_manifest.json"),
        "synthetic_truth": _read_json(output_dir / "synthetic_truth.json"),
        "metrics": metrics,
        "run_log": _read_json(output_dir / "run_log.json"),
        "research_ledger": _read_json(output_dir / "research_ledger.json"),
    }
    present: list[str] = []
    missing: list[str] = []
    for field in REQUIRED_REPRODUCIBILITY_FIELDS:
        root, nested = field.split(".", 1)
        if _has_nested(sources.get(root, {}), nested):
            present.append(field)
        else:
            missing.append(field)
    return {
        "score": len(present) / len(REQUIRED_REPRODUCIBILITY_FIELDS),
        "present": present,
        "missing": missing,
    }


def evaluate_run(output_dir: Path, metrics: dict[str, Any], validation_results: list[ValidationResult]) -> dict[str, Any]:
    output_dir = Path(output_dir)
    artifact_status = _artifact_status(output_dir)
    artifact_score = sum(1 for exists in artifact_status.values() if exists) / len(artifact_status)
    counts = _validator_counts(validation_results)
    data_validity_score = 1.0 if counts["fail"] == 0 else 0.0
    validator_score = 1.0 if counts["fail"] == 0 else 0.0

    metric_details = _model_metric_availability(metrics)
    claim_details = _report_claim_support(output_dir)
    reproducibility_details = _reproducibility_metadata(output_dir, metrics)
    sub_scores = {
        "execution_success": _sub_score(
            1.0 if artifact_score == 1.0 and data_validity_score == 1.0 else 0.0,
            {"artifact_completeness": artifact_score, "validator_failures": counts["fail"]},
        ),
        "artifact_completeness": _sub_score(
            artifact_score,
            {"artifacts": artifact_status},
        ),
        "data_validity": _sub_score(
            data_validity_score,
            {"validator_failures": counts["fail"]},
        ),
        "model_metric_availability": _sub_score(
            metric_details["score"],
            {key: value for key, value in metric_details.items() if key != "score"},
        ),
        "validator_summary": _sub_score(
            validator_score,
            {"counts": counts},
            warn_when_partial=True,
        ),
        "report_claim_support": _sub_score(
            claim_details["score"],
            {key: value for key, value in claim_details.items() if key != "score"},
        ),
        "reproducibility_metadata": _sub_score(
            reproducibility_details["score"],
            {key: value for key, value in reproducibility_details.items() if key != "score"},
        ),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "evaluation_mode": EVALUATION_MODE,
        "output_dir": str(output_dir),
        "sub_scores": sub_scores,
        "notes": [
            "Scores are deterministic offline checks for GeoSciLoop v0.1.",
            "This is not a single AI Scientist Score and does not imply real-world scientific validity.",
        ],
    }


def write_benchmark_summary(output_dir: Path, evaluation: dict[str, Any]) -> Path:
    return write_json(Path(output_dir) / "benchmark_summary.json", evaluation)
