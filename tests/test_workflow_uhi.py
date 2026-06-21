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
        "benchmark_summary.json",
        "report.md",
        "summary.md",
        "synthetic_truth.json",
        "run_log.json",
    ]
    for relative_path in expected_files:
        assert (config.output_dir / relative_path).exists(), relative_path
    assert (config.output_dir / "tables" / "synthetic_uhi_data.csv").exists()
    assert (config.output_dir / "tables" / "model_predictions.csv").exists()
    assert (config.output_dir / "figures" / "lst_distribution.png").exists()
    assert result.hard_failures == []

    metrics = json.loads((config.output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert "linear_regression" in metrics["models"]
    assert "random_forest" in metrics["models"]
    assert "benchmark" in metrics
    benchmark = json.loads((config.output_dir / "benchmark_summary.json").read_text(encoding="utf-8"))
    assert benchmark == metrics["benchmark"]
    assert benchmark["schema_version"] == "geosciloop-benchmark-v0.1"
    assert benchmark["sub_scores"]["execution_success"]["status"] == "pass"
    assert benchmark["sub_scores"]["artifact_completeness"]["score"] == 1.0
    for artifact in [
        "summary.md",
        "figures/",
        "tables/",
        "tables/synthetic_uhi_data.csv",
        "tables/model_predictions.csv",
    ]:
        assert artifact in benchmark["sub_scores"]["artifact_completeness"]["details"]["artifacts"]
    assert metrics["split_metadata"]["split_method"] == "random"
    assert metrics["split_metadata"]["test_size"] == 0.25
    assert metrics["split_metadata"]["n_train"] > 0
    assert metrics["split_metadata"]["n_test"] > 0
    assert metrics["variable_roles"]["target"] == "lst_celsius"

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
    assert ledger["variable_roles"]["target"] == "lst_celsius"
    assert ledger["synthetic_truth"]["random_seed"] == config.random_seed
    assert ledger["split_metadata"] == metrics["split_metadata"]
    assert ledger["outputs"]["summary"] == str(config.output_dir / "summary.md")
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

    summary = (config.output_dir / "summary.md").read_text(encoding="utf-8")
    for heading in [
        "## 1. What was run",
        "## 2. Run status",
        "## 3. Data used",
        "## 4. Models fitted",
        "## 5. Main results",
        "## 6. Validator outcomes",
        "## 7. Supported report claims",
        "## 8. Limitations",
        "## 9. What to do next",
    ]:
        assert heading in summary
    assert "Run succeeded" in summary
    assert "Synthetic Grid City" in summary
    assert "linear_regression" in summary
    assert "random_forest" in summary
    assert "validation_report.json" in summary
    assert "metrics.json" in summary
    assert "research_ledger.json" in summary
    assert "not evidence about a real city" in summary


def test_morphology_uhi_workflow_creates_required_artifacts_and_disciplined_claims(tmp_path):
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)
    config.output_dir = tmp_path / "uhi_morphology_synthetic_demo"

    result = run_uhi_workflow(config)

    expected_files = [
        "data_manifest.json",
        "research_plan.yaml",
        "research_ledger.json",
        "validation_report.json",
        "metrics.json",
        "benchmark_summary.json",
        "report.md",
        "summary.md",
        "synthetic_truth.json",
        "run_log.json",
    ]
    for relative_path in expected_files:
        assert (config.output_dir / relative_path).exists(), relative_path
    assert (config.output_dir / "tables" / "synthetic_uhi_data.csv").exists()
    assert (config.output_dir / "figures").is_dir()
    assert result.hard_failures == []

    manifest = json.loads((config.output_dir / "data_manifest.json").read_text(encoding="utf-8"))
    for column in [
        "building_height",
        "floor_area_ratio",
        "functional_zone",
        "population_exposure",
    ]:
        assert column in manifest["columns"]
    assert manifest["source"] == "deterministic synthetic morphology data"
    assert manifest["categorical_encodings"]["functional_zone"]["method"] == "one_hot"
    zone_manifest = manifest["categorical_encodings"]["functional_zone"]
    assert zone_manifest["allowed_categories"]
    assert zone_manifest["observed_categories"]
    assert zone_manifest["category_counts"]
    assert zone_manifest["baseline_category"]
    assert zone_manifest["encoded_columns"]
    assert manifest["synthetic_generation"]["random_seed"] == 123

    metrics = json.loads((config.output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert "linear_regression" in metrics["models"]
    assert "random_forest" in metrics["models"]
    assert metrics["feature_encoding"]["functional_zone"]["method"] == "one_hot"
    zone_metrics = metrics["feature_encoding"]["functional_zone"]
    assert zone_metrics["allowed_categories"] == zone_manifest["allowed_categories"]
    assert zone_metrics["observed_categories"] == zone_manifest["observed_categories"]
    assert zone_metrics["category_counts"] == zone_manifest["category_counts"]
    assert zone_metrics["baseline_category"] == zone_manifest["baseline_category"]
    assert any(
        feature.startswith("functional_zone_")
        for feature in metrics["models"]["random_forest"]["feature_importance"]
    )
    assert metrics["variable_roles"]["target"] == "lst_celsius"
    assert metrics["variable_roles"]["risk_indicators"] == ["population_exposure"]
    assert "population_exposure" not in metrics["split_metadata"]["model_features"]
    assert "population_exposure" not in metrics["models"]["linear_regression"]["coefficients"]
    assert "population_exposure" not in metrics["models"]["random_forest"]["feature_importance"]
    assert metrics["split_metadata"]["split_method"] == "random"
    assert metrics["split_metadata"]["test_size"] == 0.25
    assert metrics["split_metadata"]["random_seed"] == 123
    benchmark = json.loads((config.output_dir / "benchmark_summary.json").read_text(encoding="utf-8"))
    assert benchmark == metrics["benchmark"]
    artifact_status = benchmark["sub_scores"]["artifact_completeness"]["details"]["artifacts"]
    assert artifact_status["summary.md"] is True
    assert artifact_status["figures/"] is True
    assert artifact_status["tables/"] is True
    assert artifact_status["tables/synthetic_uhi_data.csv"] is True
    assert artifact_status["tables/model_predictions.csv"] is True

    synthetic_truth = json.loads((config.output_dir / "synthetic_truth.json").read_text(encoding="utf-8"))
    assert synthetic_truth["random_seed"] == 123
    assert synthetic_truth["true_coefficient_signs"]["ndvi"] == "negative"
    assert synthetic_truth["true_coefficient_signs"]["population_exposure"] == "risk_indicator"
    assert "population_exposure" in synthetic_truth["risk_indicators"]
    assert "population_exposure" not in synthetic_truth["intended_predictors"]

    validation = json.loads((config.output_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert validation["summary"]["fail"] == 0
    messages = [item["message"] for item in validation["results"]]
    warning_messages = [item["message"] for item in validation["results"] if item["status"] == "warn"]
    assert any("building_height is non-negative" in message for message in messages)
    assert any("floor_area_ratio is non-negative" in message for message in messages)
    assert any("population_exposure is non-negative" in message for message in messages)
    assert any("functional_zone values are within the allowed set" in message for message in messages)
    assert any("functional_zone categorical encoding is documented" in message for message in messages)
    assert "Random split is used on spatial grid data; spatial leakage may inflate model performance." in warning_messages
    assert any("No causal design is recorded" in message for message in warning_messages)
    assert any("High predictor correlation" in message for message in warning_messages)

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
        "warnings",
        "variable_roles",
        "synthetic_truth",
        "split_metadata",
    ]:
        assert ledger[section], section
    assert ledger["task_config"]["project_name"] == "uhi_morphology_synthetic_demo"
    assert ledger["metrics"]["feature_encoding"]["functional_zone"]["method"] == "one_hot"
    assert ledger["variable_roles"]["risk_indicators"] == ["population_exposure"]
    assert ledger["synthetic_truth"] == synthetic_truth
    assert ledger["split_metadata"] == metrics["split_metadata"]
    assert ledger["outputs"]["summary"] == str(config.output_dir / "summary.md")
    assert all(claim["supporting_artifacts"] for claim in ledger["report_claims"])
    assert any("functional_zone" in claim["claim"] for claim in ledger["report_claims"])
    assert any("population_exposure" in claim["claim"] for claim in ledger["report_claims"])

    report = (config.output_dir / "report.md").read_text(encoding="utf-8")
    for heading in [
        "## Research question",
        "## Synthetic demo disclaimer",
        "## Variables and methods",
        "## Model results",
        "## Supported claims",
        "## Unsupported or warned claims",
        "## Validation summary",
        "## Limitations",
        "## Future real remote-sensing/GIS mapping",
    ]:
        assert heading in report
    assert "not evidence about a real city" in report
    assert "real-world" not in report.lower().replace("real-world claims", "")
    assert "population_exposure" in report
    assert "functional_zone" in report
    assert "does not reduce building_height to a simple directional heat conclusion" in report
    assert "Predictors used for LST modeling" in report
    assert "Risk indicators not used as default LST predictors" in report
    assert "Random split is used on spatial grid data" in report
    assert "population_exposure is included as a synthetic heat-risk relevance indicator" in report
    assert "population_exposure predicts LST" not in report
    assert "population_exposure causes" not in report

    summary = (config.output_dir / "summary.md").read_text(encoding="utf-8")
    assert "Synthetic Morphology City" in summary
    assert "Run succeeded" in summary
    assert "main findings" in summary.lower()
    assert "warnings mean" in summary.lower()
    assert "Human-readable files" in summary
    assert "Developer/audit files" in summary
    assert "not evidence about a real city" in summary
    assert "Risk indicators" in summary
    assert "Random split is used on spatial grid data" in summary
