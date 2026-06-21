import json
from pathlib import Path

from geosciloop.benchmark.evaluator import evaluate_dry_run, evaluate_run, write_benchmark_summary
from geosciloop.core.state import ValidationResult


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _create_complete_output_dir(output_dir: Path) -> None:
    (output_dir / "figures").mkdir(parents=True)
    (output_dir / "tables").mkdir(parents=True)
    for name in [
        "research_plan.yaml",
        "report.md",
        "summary.md",
    ]:
        (output_dir / name).write_text("synthetic output", encoding="utf-8")
    for name in [
        "tables/synthetic_uhi_data.csv",
        "tables/model_predictions.csv",
    ]:
        (output_dir / name).write_text("cell_id,lst_celsius\n1,35\n", encoding="utf-8")

    _write_json(output_dir / "data_manifest.json", {"random_seed": 42, "offline": True})
    _write_json(output_dir / "synthetic_truth.json", {"random_seed": 42, "true_coefficient_signs": {"ndvi": "negative"}})
    _write_json(output_dir / "validation_report.json", {"summary": {"pass": 2, "warn": 1, "fail": 0}})
    _write_json(output_dir / "run_log.json", {"offline": True, "split_metadata": {"split_method": "random"}})
    _write_json(
        output_dir / "research_ledger.json",
        {
            "task_config": {"project_name": "demo"},
            "data_manifest": {"random_seed": 42},
            "metrics": {"models": {}},
            "validation_results": [{"name": "demo", "status": "pass", "message": "ok", "details": {}}],
            "report_claims": [
                {
                    "claim": "NDVI is negatively associated with synthetic LST.",
                    "support_status": "supported",
                    "supporting_artifacts": ["metrics.json"],
                    "supporting_validation": ["NDVI negative association"],
                    "evidence": {"correlation": -0.5},
                }
            ],
            "variable_roles": {"target": "lst_celsius", "predictors": ["ndvi"], "risk_indicators": []},
            "synthetic_truth": {"random_seed": 42},
            "split_metadata": {"split_method": "random", "random_seed": 42, "n_train": 3, "n_test": 1},
        },
    )
    _write_json(output_dir / "metrics.json", {"models": {}})


def _complete_metrics() -> dict:
    return {
        "models": {
            "linear_regression": {"r2": 0.7, "rmse": 1.2, "mae": 0.9},
            "random_forest": {"r2": 0.8, "rmse": 1.0, "mae": 0.7},
        },
        "variable_roles": {"target": "lst_celsius", "predictors": ["ndvi"], "risk_indicators": []},
        "split_metadata": {
            "split_method": "random",
            "test_size": 0.25,
            "random_seed": 42,
            "n_train": 3,
            "n_test": 1,
            "model_features": ["ndvi"],
        },
    }


def test_evaluate_run_returns_decomposed_offline_subscores(tmp_path):
    _create_complete_output_dir(tmp_path)
    validation_results = [
        ValidationResult("schema", "pass", "ok"),
        ValidationResult("spatial_split", "warn", "Random split warning."),
    ]

    evaluation = evaluate_run(tmp_path, _complete_metrics(), validation_results)

    assert evaluation["schema_version"] == "geosciloop-benchmark-v0.1"
    assert evaluation["evaluation_mode"] == "offline_v0_1"
    assert "ai_scientist_score" not in evaluation
    assert set(evaluation["sub_scores"]) == {
        "execution_success",
        "artifact_completeness",
        "data_validity",
        "model_metric_availability",
        "validator_summary",
        "report_claim_support",
        "reproducibility_metadata",
    }
    for sub_score in evaluation["sub_scores"].values():
        assert {"score", "status", "details"}.issubset(sub_score)
    assert evaluation["sub_scores"]["execution_success"]["status"] == "pass"
    assert evaluation["sub_scores"]["artifact_completeness"]["score"] == 1.0
    assert evaluation["sub_scores"]["data_validity"]["status"] == "pass"
    assert evaluation["sub_scores"]["validator_summary"]["details"]["counts"] == {"pass": 1, "warn": 1, "fail": 0}
    assert evaluation["sub_scores"]["report_claim_support"]["status"] == "pass"
    assert evaluation["sub_scores"]["reproducibility_metadata"]["status"] == "pass"


def test_evaluate_run_detects_missing_artifacts_and_reproducibility_gaps(tmp_path):
    _create_complete_output_dir(tmp_path)
    (tmp_path / "summary.md").unlink()
    (tmp_path / "synthetic_truth.json").unlink()
    validation_results = [ValidationResult("value_ranges", "fail", "bad values")]

    evaluation = evaluate_run(
        tmp_path,
        {"models": {"linear_regression": {"r2": 0.2}}},
        validation_results,
    )

    assert evaluation["sub_scores"]["execution_success"]["status"] == "fail"
    assert evaluation["sub_scores"]["artifact_completeness"]["status"] == "fail"
    assert evaluation["sub_scores"]["artifact_completeness"]["details"]["artifacts"]["summary.md"] is False
    assert evaluation["sub_scores"]["data_validity"]["status"] == "fail"
    assert evaluation["sub_scores"]["model_metric_availability"]["status"] == "fail"
    assert evaluation["sub_scores"]["reproducibility_metadata"]["status"] == "fail"


def test_write_benchmark_summary_writes_json(tmp_path):
    _create_complete_output_dir(tmp_path)
    evaluation = evaluate_run(tmp_path, _complete_metrics(), [ValidationResult("schema", "pass", "ok")])

    path = write_benchmark_summary(tmp_path, evaluation)

    assert path == tmp_path / "benchmark_summary.json"
    assert json.loads(path.read_text(encoding="utf-8")) == evaluation


def test_evaluate_dry_run_returns_v0_2_subscores(tmp_path):
    for name in [
        "adapter_plan.json",
        "data_source_manifest.json",
        "metadata_validation_report.json",
        "validation_report.json",
        "research_ledger.json",
        "dry_run_report.md",
        "summary.md",
        "run_log.json",
    ]:
        (tmp_path / name).write_text("{}", encoding="utf-8")
    (tmp_path / "dry_run_report.md").write_text("Dry-run disclaimer. No data were downloaded.", encoding="utf-8")
    (tmp_path / "summary.md").write_text("No data were downloaded.", encoding="utf-8")
    _write_json(
        tmp_path / "adapter_plan.json",
        {"plans": [{"role": "lst", "adapter": "fixture_stac", "dry_run": True}]},
    )
    _write_json(
        tmp_path / "data_source_manifest.json",
        {
            "schema_version": "geosciloop-data-source-manifest-v0.2",
            "offline": True,
            "dry_run": True,
            "sources": [
                {
                    "role": "lst",
                    "provider": "USGS",
                    "collection": "landsat-c2-l2",
                    "dataset": "landsat_l2",
                    "datetime": "2024-07-15T10:00:00Z",
                    "license": "USGS public domain",
                    "href": "mock://landsat/l2/ST_B10.tif",
                    "query": {"bbox": [0, 1, 2, 3]},
                    "provenance": {"fixture": "stac_landsat_l2_item.json"},
                    "downloaded": False,
                    "requires_credentials": False,
                }
            ],
        },
    )
    _write_json(
        tmp_path / "research_ledger.json",
        {
            "dry_run": True,
            "download_performed": False,
            "credentials_required": False,
            "adapter_plans": [{"role": "lst"}],
            "data_source_manifest": {"sources": [{"role": "lst"}]},
            "metadata_validation_results": [{"name": "crs_metadata", "status": "pass", "message": "ok", "details": {}}],
            "outputs": {"summary": str(tmp_path / "summary.md")},
        },
    )
    _write_json(tmp_path / "run_log.json", {"offline": True, "dry_run": True, "download_performed": False, "credentials_required": False})
    validation_results = [
        ValidationResult("crs_metadata", "pass", "ok"),
        ValidationResult("split_strategy", "warn", "spatial leakage warning"),
    ]

    evaluation = evaluate_dry_run(tmp_path, validation_results)

    assert evaluation["schema_version"] == "geosciloop-benchmark-v0.2-dry-run"
    assert evaluation["evaluation_mode"] == "fixture_real_data_dry_run_v0_2"
    assert "ai_scientist_score" not in evaluation
    assert evaluation["sub_scores"]["execution_success"]["status"] == "pass"
    assert evaluation["sub_scores"]["no_live_dependency_check"]["status"] == "pass"
