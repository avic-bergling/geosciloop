from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path

from geosciloop.adapters.registry import build_adapter
from geosciloop.benchmark.evaluator import evaluate_dry_run, write_benchmark_summary
from geosciloop.core.artifact_store import ensure_dir, to_jsonable, write_json
from geosciloop.core.ledger import ResearchLedger
from geosciloop.core.schema import DataSourceManifest, TaskConfig
from geosciloop.core.state import WorkflowResult
from geosciloop.report.dry_run_writer import write_dry_run_report, write_dry_run_summary
from geosciloop.validators.metadata import run_metadata_validators


def _validation_report(validation_results) -> dict:
    payload = [result.to_dict() for result in validation_results]
    summary = {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }
    return {
        "status_levels": ["pass", "warn", "fail"],
        "summary": summary,
        "results": payload,
    }


def _report_claims() -> list[dict]:
    return [
        {
            "claim": "The dry-run planned fixture-backed data sources without downloading data.",
            "support_status": "supported",
            "supporting_artifacts": ["adapter_plan.json", "data_source_manifest.json", "run_log.json"],
            "supporting_validation": ["no_live_dependency_check"],
            "evidence": {"download_performed": False, "credentials_required": False},
        },
        {
            "claim": "The dry-run produced deterministic metadata validation records.",
            "support_status": "supported",
            "supporting_artifacts": ["metadata_validation_report.json", "validation_report.json"],
            "supporting_validation": ["metadata validators"],
            "evidence": {"status_levels": ["pass", "warn", "fail"]},
        },
    ]


def _limitations() -> list[str]:
    return [
        "Fixture metadata is not authoritative provider metadata.",
        "No raster pixels, vector geometries, or population grid values were downloaded or processed.",
        "Metadata validation checks planning completeness, not real-world scientific validity.",
        "Random split is included to surface spatial leakage risk before real geospatial modeling.",
        "LST is land surface temperature, not air temperature.",
    ]


def run_real_data_dry_run(config: TaskConfig) -> WorkflowResult:
    if not config.offline:
        raise ValueError("v0.2 dry-run must run offline=true")
    if not config.dry_run:
        raise ValueError("v0.2 real-data adapter prototype requires dry_run=true")
    if config.execution.get("download") is True:
        raise ValueError("v0.2 dry-run template cannot download data")
    if config.execution.get("require_credentials") is True:
        raise ValueError("v0.2 dry-run template cannot require credentials")

    start = time.time()
    output_dir = ensure_dir(config.output_dir)
    artifacts: dict[str, str] = {}

    adapter_plans = []
    records = []
    for request in config.data_sources:
        adapter = build_adapter(request.adapter)
        plan = adapter.plan(request)
        adapter_plans.append(to_jsonable(plan))
        for item in adapter.search(request):
            records.append(adapter.describe(item, request=request))

    adapter_plan_payload = {
        "schema_version": "geosciloop-adapter-plan-v0.2",
        "project_name": config.project_name,
        "mode": config.mode,
        "offline": config.offline,
        "dry_run": config.dry_run,
        "plans": adapter_plans,
    }
    write_json(output_dir / "adapter_plan.json", adapter_plan_payload)
    artifacts["adapter_plan"] = str(output_dir / "adapter_plan.json")

    manifest = DataSourceManifest(
        schema_version="geosciloop-data-source-manifest-v0.2",
        project_name=config.project_name,
        mode=config.mode,
        offline=config.offline,
        dry_run=config.dry_run,
        sources=records,
        split_strategy=config.split_strategy,
        metadata_plan=config.metadata_plan,
    )
    manifest_payload = to_jsonable(manifest)
    write_json(output_dir / "data_source_manifest.json", manifest_payload)
    artifacts["data_source_manifest"] = str(output_dir / "data_source_manifest.json")

    validation_results = run_metadata_validators(manifest)
    validation_report = _validation_report(validation_results)
    write_json(output_dir / "metadata_validation_report.json", validation_report)
    write_json(output_dir / "validation_report.json", validation_report)
    artifacts["metadata_validation_report"] = str(output_dir / "metadata_validation_report.json")
    artifacts["validation_report"] = str(output_dir / "validation_report.json")

    report_path = output_dir / "dry_run_report.md"
    write_dry_run_report(config, adapter_plan_payload, manifest_payload, validation_report, report_path)
    artifacts["dry_run_report"] = str(report_path)

    summary_path = output_dir / "summary.md"
    write_dry_run_summary(config, manifest_payload, validation_report, None, artifacts, summary_path)
    artifacts["summary"] = str(summary_path)

    run_log = {
        "project_name": config.project_name,
        "mode": config.mode,
        "offline": config.offline,
        "dry_run": config.dry_run,
        "download_performed": False,
        "credentials_required": False,
        "output_dir": str(output_dir),
        "elapsed_seconds": round(time.time() - start, 3),
        "hard_failures": [result.to_dict() for result in validation_results if result.status == "fail"],
    }
    write_json(output_dir / "run_log.json", run_log)
    artifacts["run_log"] = str(output_dir / "run_log.json")

    ledger = ResearchLedger.from_config(config)
    ledger.record_step("plan", "Build fixture-backed adapter plans from the dry-run config.")
    ledger.record_step("manifest", "Convert fixture metadata into a data source manifest.")
    ledger.record_step("validate", "Run deterministic metadata validators.")
    ledger.record_step("report", "Write dry-run report and summary from artifacts.")
    ledger.dry_run = True
    ledger.download_performed = False
    ledger.credentials_required = False
    ledger.aoi = asdict(config.aoi)
    ledger.time_range = asdict(config.time_range)
    ledger.variable_roles = config.variable_roles()
    ledger.data_source_requests = [to_jsonable(request) for request in config.data_sources]
    ledger.adapter_plans = adapter_plans
    ledger.data_source_manifest = manifest_payload
    ledger.data_manifest = manifest_payload
    ledger.validation_results = validation_report["results"]
    ledger.validation_summary = validation_report["summary"]
    ledger.metadata_validation_results = validation_report["results"]
    ledger.metadata_validation_summary = validation_report["summary"]
    ledger.report_claims = _report_claims()
    ledger.limitations = _limitations()
    ledger.warnings = [result.to_dict() for result in validation_results if result.status == "warn"]
    ledger.outputs = {
        **artifacts,
        "research_ledger": str(output_dir / "research_ledger.json"),
        "benchmark_summary": str(output_dir / "benchmark_summary.json"),
    }
    ledger.benchmark_summary = {"status": "pending"}
    ledger.write(output_dir / "research_ledger.json")
    artifacts["research_ledger"] = str(output_dir / "research_ledger.json")

    benchmark = evaluate_dry_run(output_dir, validation_results)
    write_benchmark_summary(output_dir, benchmark)
    artifacts["benchmark_summary"] = str(output_dir / "benchmark_summary.json")

    write_dry_run_summary(config, manifest_payload, validation_report, benchmark, artifacts, summary_path)
    ledger.outputs = artifacts
    ledger.benchmark_summary = benchmark
    ledger.metrics = {"benchmark": benchmark}
    ledger.write(output_dir / "research_ledger.json")

    return WorkflowResult(output_dir=Path(output_dir), validation_results=validation_results, metrics={"benchmark": benchmark}, artifacts=artifacts)
