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
DRY_RUN_SCHEMA_VERSION = "geosciloop-benchmark-v0.2-dry-run"
DRY_RUN_EVALUATION_MODE = "fixture_real_data_dry_run_v0_2"
REQUIRED_DRY_RUN_ARTIFACTS = {
    "adapter_plan.json": "file",
    "data_source_manifest.json": "file",
    "metadata_validation_report.json": "file",
    "validation_report.json": "file",
    "research_ledger.json": "file",
    "dry_run_report.md": "file",
    "summary.md": "file",
    "run_log.json": "file",
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


def _dry_run_artifact_status(output_dir: Path) -> dict[str, bool]:
    return {
        artifact: (output_dir / artifact).is_dir() if artifact_type == "dir" else (output_dir / artifact).is_file()
        for artifact, artifact_type in REQUIRED_DRY_RUN_ARTIFACTS.items()
    }


def _score_bool_map(status: dict[str, bool]) -> float:
    return sum(1 for exists in status.values() if exists) / len(status) if status else 0.0


def _manifest_completeness(manifest: dict[str, Any]) -> dict[str, Any]:
    required_top = ["schema_version", "project_name", "mode", "offline", "dry_run", "sources"]
    present_top = [field for field in required_top if _has_nested(manifest, field)]
    sources = manifest.get("sources", [])
    source_required = ["role", "provider", "datetime", "license", "href", "query", "provenance", "downloaded", "requires_credentials"]
    source_scores = []
    missing_by_role = {}
    for source in sources:
        missing = [field for field in source_required if field not in source or source[field] in (None, "", [], {})]
        if not (source.get("collection") or source.get("dataset")):
            missing.append("collection_or_dataset")
        source_scores.append((len(source_required) + 1 - len(missing)) / (len(source_required) + 1))
        if missing:
            missing_by_role[source.get("role", "unknown")] = missing
    top_score = len(present_top) / len(required_top)
    source_score = sum(source_scores) / len(source_scores) if source_scores else 0.0
    return {
        "score": (top_score + source_score) / 2,
        "present_top_fields": present_top,
        "missing_top_fields": [field for field in required_top if field not in present_top],
        "missing_by_role": missing_by_role,
        "source_count": len(sources),
    }


def _adapter_plan_completeness(adapter_plan: dict[str, Any]) -> dict[str, Any]:
    plans = adapter_plan.get("plans", [])
    if not plans:
        return {"score": 0.0, "plan_count": 0, "missing_by_role": {"all": ["plans"]}}
    required = ["role", "adapter", "provider", "dry_run", "download", "requires_credentials", "fixture"]
    missing_by_role = {}
    scores = []
    for plan in plans:
        missing = [field for field in required if field not in plan or plan[field] in (None, "", [], {})]
        scores.append((len(required) - len(missing)) / len(required))
        if missing:
            missing_by_role[plan.get("role", "unknown")] = missing
    return {"score": sum(scores) / len(scores), "plan_count": len(plans), "missing_by_role": missing_by_role}


def _provenance_completeness(manifest: dict[str, Any]) -> dict[str, Any]:
    sources = manifest.get("sources", [])
    required = ["provider", "datetime", "license", "href", "query", "provenance"]
    missing_by_role = {}
    scores = []
    for source in sources:
        missing = [field for field in required if not source.get(field)]
        if not (source.get("collection") or source.get("dataset")):
            missing.append("collection_or_dataset")
        scores.append((len(required) + 1 - len(missing)) / (len(required) + 1))
        if missing:
            missing_by_role[source.get("role", "unknown")] = missing
    return {"score": sum(scores) / len(scores) if scores else 0.0, "missing_by_role": missing_by_role}


def _ledger_completeness(ledger: dict[str, Any]) -> dict[str, Any]:
    required = [
        "task_config",
        "adapter_plans",
        "data_source_manifest",
        "metadata_validation_results",
        "benchmark_summary",
        "outputs",
        "report_claims",
        "limitations",
    ]
    present = [field for field in required if _has_nested(ledger, field)]
    flags_ok = (
        ledger.get("dry_run") is True
        and ledger.get("download_performed") is False
        and ledger.get("credentials_required") is False
    )
    score = (len(present) + (1 if flags_ok else 0)) / (len(required) + 1)
    return {
        "score": score,
        "present": present,
        "missing": [field for field in required if field not in present],
        "flags_ok": flags_ok,
    }


def _dry_run_reproducibility(manifest: dict[str, Any], run_log: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "manifest_offline": manifest.get("offline") is True,
        "manifest_dry_run": manifest.get("dry_run") is True,
        "run_log_offline": run_log.get("offline") is True,
        "run_log_dry_run": run_log.get("dry_run") is True,
        "download_performed_false": run_log.get("download_performed") is False,
        "credentials_required_false": run_log.get("credentials_required") is False,
    }
    return {"score": sum(1 for ok in checks.values() if ok) / len(checks), "checks": checks}


def _report_disclaimer_quality(output_dir: Path) -> dict[str, Any]:
    report = (output_dir / "dry_run_report.md").read_text(encoding="utf-8") if (output_dir / "dry_run_report.md").is_file() else ""
    summary = (output_dir / "summary.md").read_text(encoding="utf-8") if (output_dir / "summary.md").is_file() else ""
    combined = f"{report}\n{summary}".lower()
    checks = {
        "mentions_dry_run": "dry-run" in combined or "dry run" in combined,
        "mentions_no_download": "no data were downloaded" in combined,
        "rejects_real_world_claim": "not a real-world uhi conclusion" in combined
        or "no real-world scientific claims" in combined,
    }
    return {"score": sum(1 for ok in checks.values() if ok) / len(checks), "checks": checks}


def _no_live_dependency_check(manifest: dict[str, Any], run_log: dict[str, Any]) -> dict[str, Any]:
    sources = manifest.get("sources", [])
    checks = {
        "run_log_download_false": run_log.get("download_performed") is False,
        "run_log_credentials_false": run_log.get("credentials_required") is False,
        "all_sources_not_downloaded": all(source.get("downloaded") is False for source in sources),
        "all_sources_no_credentials": all(source.get("requires_credentials") is False for source in sources),
        "all_hrefs_mock": all(str(source.get("href", "")).startswith("mock://") for source in sources),
    }
    return {"score": sum(1 for ok in checks.values() if ok) / len(checks), "checks": checks}


def evaluate_dry_run(output_dir: Path, validation_results: list[ValidationResult]) -> dict[str, Any]:
    output_dir = Path(output_dir)
    artifact_status = _dry_run_artifact_status(output_dir)
    artifact_score = _score_bool_map(artifact_status)
    counts = _validator_counts(validation_results)
    validation_score = 1.0 if counts["fail"] == 0 else 0.0
    manifest = _read_json(output_dir / "data_source_manifest.json")
    adapter_plan = _read_json(output_dir / "adapter_plan.json")
    ledger = _read_json(output_dir / "research_ledger.json")
    run_log = _read_json(output_dir / "run_log.json")
    manifest_details = _manifest_completeness(manifest)
    provenance_details = _provenance_completeness(manifest)
    adapter_details = _adapter_plan_completeness(adapter_plan)
    ledger_details = _ledger_completeness(ledger)
    reproducibility_details = _dry_run_reproducibility(manifest, run_log)
    disclaimer_details = _report_disclaimer_quality(output_dir)
    no_live_details = _no_live_dependency_check(manifest, run_log)

    sub_scores = {
        "execution_success": _sub_score(
            1.0 if artifact_score == 1.0 and validation_score == 1.0 and no_live_details["score"] == 1.0 else 0.0,
            {"artifact_completeness": artifact_score, "validator_failures": counts["fail"], "no_live_dependency_score": no_live_details["score"]},
        ),
        "artifact_completeness": _sub_score(artifact_score, {"artifacts": artifact_status}),
        "data_source_manifest_completeness": _sub_score(
            manifest_details["score"],
            {key: value for key, value in manifest_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "metadata_validation_status": _sub_score(
            validation_score,
            {"counts": counts},
            warn_when_partial=True,
        ),
        "provenance_completeness": _sub_score(
            provenance_details["score"],
            {key: value for key, value in provenance_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "adapter_plan_completeness": _sub_score(
            adapter_details["score"],
            {key: value for key, value in adapter_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "ledger_completeness": _sub_score(
            ledger_details["score"],
            {key: value for key, value in ledger_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "reproducibility": _sub_score(
            reproducibility_details["score"],
            {key: value for key, value in reproducibility_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "report_disclaimer_quality": _sub_score(
            disclaimer_details["score"],
            {key: value for key, value in disclaimer_details.items() if key != "score"},
            warn_when_partial=True,
        ),
        "no_live_dependency_check": _sub_score(
            no_live_details["score"],
            {key: value for key, value in no_live_details.items() if key != "score"},
            warn_when_partial=True,
        ),
    }
    return {
        "schema_version": DRY_RUN_SCHEMA_VERSION,
        "evaluation_mode": DRY_RUN_EVALUATION_MODE,
        "output_dir": str(output_dir),
        "sub_scores": sub_scores,
        "notes": [
            "Scores are deterministic offline checks for GeoSciLoop v0.2 dry-run planning.",
            "This is not a single AI Scientist Score and does not imply real-world scientific validity.",
            "The dry-run evaluator checks metadata and provenance planning artifacts, not real raster or vector data quality.",
        ],
    }
