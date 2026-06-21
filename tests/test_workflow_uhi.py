import json
from pathlib import Path

from geosciloop.core.schema import load_task_config
from geosciloop.workflows.urban_heat_island import run_uhi_workflow


def test_uhi_workflow_creates_required_artifacts(tmp_path):
    config = load_task_config("configs/uhi_synthetic_demo.yaml", offline_override=True)
    config.output_dir = tmp_path / "uhi_synthetic_demo"

    result = run_uhi_workflow(config)

    expected_files = [
        "data_manifest.json",
        "research_plan.yaml",
        "research_ledger.json",
        "validation_report.json",
        "metrics.json",
        "report.md",
        "run_log.json",
    ]
    for relative_path in expected_files:
        assert (config.output_dir / relative_path).exists(), relative_path
    assert (config.output_dir / "tables" / "synthetic_uhi_data.csv").exists()
    assert (config.output_dir / "figures" / "lst_distribution.png").exists()
    assert result.hard_failures == []

    metrics = json.loads((config.output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert "linear_regression" in metrics["models"]
    assert "random_forest" in metrics["models"]
    assert "benchmark" in metrics
    assert metrics["benchmark"]["execution_success"] is True
    assert all(metrics["benchmark"]["artifact_completeness"].values())

    validation = json.loads((config.output_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert validation["status_levels"] == ["pass", "warn", "fail"]
    assert validation["summary"]["pass"] > 0
    assert validation["summary"]["warn"] > 0
    assert validation["summary"]["fail"] == 0
    statuses = {result["status"] for result in validation["results"]}
    assert {"pass", "warn"}.issubset(statuses)
    assert all({"name", "status", "message", "details"}.issubset(result) for result in validation["results"])

    ledger = json.loads((config.output_dir / "research_ledger.json").read_text(encoding="utf-8"))
    for section in [
        "task_config",
        "generated_hypotheses",
        "data_manifest",
        "workflow_steps",
        "outputs",
        "validation_results",
        "metrics",
        "report_claims",
    ]:
        assert ledger[section], section
    assert ledger["task_config"]["project_name"] == config.project_name
    assert ledger["metrics"]["models"]["linear_regression"]["r2"] == metrics["models"]["linear_regression"]["r2"]
    assert ledger["validation_results"] == validation["results"]
    for claim in ledger["report_claims"]:
        assert claim["support_status"] == "supported"
        assert claim["supporting_artifacts"]
        assert claim["supporting_validation"]
        assert claim["evidence"]

    report = (config.output_dir / "report.md").read_text(encoding="utf-8")
    assert "Synthetic demo disclaimer" in report
    assert "not evidence about a real city" in report
    assert "not the same as air temperature" in report
    assert "Artifact trail" in report
