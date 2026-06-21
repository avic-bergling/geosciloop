import json
import subprocess
import sys
from pathlib import Path

from geosciloop.core.runner import run_config
from geosciloop.core.schema import load_task_config


def test_real_pilot_dry_run_workflow_creates_required_artifacts(tmp_path):
    config = load_task_config("configs/uhi_real_pilot_template.yaml", dry_run_override=True)
    config.output_dir = tmp_path / "uhi_real_pilot_template"

    result = run_config(config)

    expected_files = [
        "adapter_plan.json",
        "data_source_manifest.json",
        "metadata_validation_report.json",
        "validation_report.json",
        "research_ledger.json",
        "dry_run_report.md",
        "summary.md",
        "benchmark_summary.json",
        "run_log.json",
    ]
    for relative_path in expected_files:
        assert (config.output_dir / relative_path).exists(), relative_path
    assert result.hard_failures == []

    manifest = json.loads((config.output_dir / "data_source_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "geosciloop-data-source-manifest-v0.2"
    assert manifest["project_name"] == "uhi_real_pilot_template"
    assert manifest["offline"] is True
    assert manifest["dry_run"] is True
    assert len(manifest["sources"]) == 4
    assert {source["role"] for source in manifest["sources"]} == {"lst", "optical", "roads", "population"}
    assert all(source["downloaded"] is False for source in manifest["sources"])
    assert all(source["requires_credentials"] is False for source in manifest["sources"])

    validation = json.loads((config.output_dir / "metadata_validation_report.json").read_text(encoding="utf-8"))
    assert validation["summary"]["fail"] == 0
    assert validation["summary"]["warn"] >= 1
    assert any(result["name"] == "split_strategy" and result["status"] == "warn" for result in validation["results"])

    ledger = json.loads((config.output_dir / "research_ledger.json").read_text(encoding="utf-8"))
    assert ledger["dry_run"] is True
    assert ledger["download_performed"] is False
    assert ledger["credentials_required"] is False
    assert ledger["adapter_plans"]
    assert ledger["data_source_manifest"]["sources"]
    assert ledger["metadata_validation_results"] == validation["results"]
    assert ledger["outputs"]["summary"] == str(config.output_dir / "summary.md")

    benchmark = json.loads((config.output_dir / "benchmark_summary.json").read_text(encoding="utf-8"))
    assert benchmark["schema_version"] == "geosciloop-benchmark-v0.2-dry-run"
    assert set(benchmark["sub_scores"]) == {
        "execution_success",
        "artifact_completeness",
        "data_source_manifest_completeness",
        "metadata_validation_status",
        "provenance_completeness",
        "adapter_plan_completeness",
        "ledger_completeness",
        "reproducibility",
        "report_disclaimer_quality",
        "no_live_dependency_check",
    }

    summary = (config.output_dir / "summary.md").read_text(encoding="utf-8")
    dry_run_report = (config.output_dir / "dry_run_report.md").read_text(encoding="utf-8")
    assert "No data were downloaded" in summary
    assert "dry-run" in dry_run_report.lower()
    assert "not a real-world UHI conclusion" in dry_run_report


def test_dry_run_cli_works_without_credentials_or_network(tmp_path):
    output_dir = tmp_path / "cli_dry_run"
    command = [
        sys.executable,
        "-m",
        "geosciloop.cli",
        "run",
        "configs/uhi_real_pilot_template.yaml",
        "--dry-run",
        "--output-dir",
        str(output_dir),
    ]

    completed = subprocess.run(command, check=False, capture_output=True, text=True)

    assert completed.returncode == 0, completed.stderr
    assert "GeoSciLoop run complete" in completed.stdout
    assert (output_dir / "data_source_manifest.json").exists()
    run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
    assert run_log["dry_run"] is True
    assert run_log["download_performed"] is False
    assert run_log["credentials_required"] is False


def test_outputs_directory_remains_gitignored():
    command = ["git", "check-ignore", "outputs/uhi_real_pilot_template/data_source_manifest.json"]

    completed = subprocess.run(command, check=False, capture_output=True, text=True)

    assert completed.returncode == 0
    assert completed.stdout.strip() == "outputs/uhi_real_pilot_template/data_source_manifest.json"
