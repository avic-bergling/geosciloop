from __future__ import annotations

import time
from pathlib import Path

from geosciloop.agents.critic import summarize_warnings
from geosciloop.agents.planner import write_research_plan
from geosciloop.agents.writer import write_report
from geosciloop.benchmark.evaluator import evaluate_run
from geosciloop.benchmark.evaluator import write_benchmark_summary
from geosciloop.core.artifact_store import ensure_dir, write_json
from geosciloop.core.ledger import ResearchLedger
from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import WorkflowResult
from geosciloop.report.markdown_writer import build_preliminary_claims
from geosciloop.report.summary_writer import write_summary
from geosciloop.tools.modeling import fit_models
from geosciloop.tools.plotting import save_figures
from geosciloop.tools.synthetic_data import ALLOWED_FUNCTIONAL_ZONES
from geosciloop.tools.synthetic_data import build_synthetic_truth
from geosciloop.tools.synthetic_data import create_synthetic_uhi_data
from geosciloop.validators.validator_suite import run_validator_suite


def run_uhi_workflow(config: TaskConfig) -> WorkflowResult:
    start = time.time()
    output_dir = ensure_dir(config.output_dir)
    tables_dir = ensure_dir(output_dir / "tables")
    figures_dir = ensure_dir(output_dir / "figures")
    artifacts: dict[str, str] = {}

    ledger = ResearchLedger.from_config(config)
    variable_roles = config.variable_roles()
    ledger.variable_roles = variable_roles
    ledger.record_step("plan", "Create deterministic research plan from config.")
    plan = write_research_plan(config, output_dir / "research_plan.yaml")
    artifacts["research_plan"] = str(output_dir / "research_plan.yaml")
    ledger.generated_hypotheses = list(plan["hypotheses"])

    ledger.record_step("data", "Generate deterministic synthetic UHI grid table.")
    data = create_synthetic_uhi_data(config)
    data_path = tables_dir / "synthetic_uhi_data.csv"
    data.to_csv(data_path, index=False)
    artifacts["synthetic_data"] = str(data_path)

    synthetic_truth = build_synthetic_truth(config)
    write_json(output_dir / "synthetic_truth.json", synthetic_truth)
    artifacts["synthetic_truth"] = str(output_dir / "synthetic_truth.json")
    ledger.synthetic_truth = synthetic_truth

    ledger.record_step("model", "Fit linear regression and random forest models.")
    model_metrics, predictions = fit_models(data, config)
    prediction_path = tables_dir / "model_predictions.csv"
    predictions.to_csv(prediction_path, index=False)
    artifacts["model_predictions"] = str(prediction_path)

    figure_artifacts = save_figures(data, predictions, model_metrics, figures_dir)
    artifacts.update(figure_artifacts)

    evidence = {
        "linear_regression": model_metrics.get("linear_regression", {}),
        "correlations": model_metrics.get("correlations", {}),
        "feature_encoding": model_metrics.get("feature_encoding", {}),
        "split_metadata": model_metrics.get("split_metadata", {}),
        "model_features": model_metrics.get("split_metadata", {}).get("model_features", []),
    }
    preliminary_claims = build_preliminary_claims(config)
    model_only_metrics = {
        key: value
        for key, value in model_metrics.items()
        if key not in {"correlations", "feature_encoding", "split_metadata"}
    }
    validation_results = run_validator_suite(config, data, model_only_metrics, preliminary_claims, evidence)
    validation_payload = [result.to_dict() for result in validation_results]
    validation_summary = {
        status: sum(1 for result in validation_results if result.status == status)
        for status in ["pass", "warn", "fail"]
    }
    validation_report = {
        "status_levels": ["pass", "warn", "fail"],
        "summary": validation_summary,
        "results": validation_payload,
    }
    write_json(output_dir / "validation_report.json", validation_report)
    artifacts["validation_report"] = str(output_dir / "validation_report.json")

    data_manifest = {
        "source": "deterministic synthetic morphology data"
        if "functional_zone" in data.columns
        else "deterministic synthetic data",
        "n_rows": int(len(data)),
        "columns": list(data.columns),
        "random_seed": config.random_seed,
        "offline": config.offline,
        "artifact": str(data_path),
        "variable_roles": variable_roles,
        "synthetic_generation": synthetic_truth,
    }
    if "functional_zone" in data.columns:
        data_manifest["categorical_encodings"] = {
            "functional_zone": {
                **model_metrics.get("feature_encoding", {}).get("functional_zone", {}),
                "allowed_categories": list(ALLOWED_FUNCTIONAL_ZONES),
            }
        }
    write_json(output_dir / "data_manifest.json", data_manifest)
    artifacts["data_manifest"] = str(output_dir / "data_manifest.json")
    ledger.data_manifest = data_manifest

    metrics_payload = {"models": model_only_metrics}
    metrics_payload["correlations"] = model_metrics["correlations"]
    if model_metrics.get("feature_encoding"):
        metrics_payload["feature_encoding"] = model_metrics["feature_encoding"]
    metrics_payload["variable_roles"] = variable_roles
    metrics_payload["split_metadata"] = model_metrics["split_metadata"]
    # Benchmark initially checks artifacts created before report and ledger; update after remaining writes.
    write_json(output_dir / "metrics.json", metrics_payload)
    artifacts["metrics"] = str(output_dir / "metrics.json")

    critic_summary = summarize_warnings(validation_results, {"models": metrics_payload["models"]})
    _, report_claims = write_report(
        config,
        plan,
        metrics_payload,
        validation_results,
        critic_summary,
        output_dir / "report.md",
    )
    artifacts["report"] = str(output_dir / "report.md")

    summary_path = output_dir / "summary.md"
    write_summary(
        config=config,
        data_manifest=data_manifest,
        metrics=metrics_payload,
        validation_report=validation_report,
        report_claims=report_claims,
        critic_summary=critic_summary,
        artifacts={
            **artifacts,
            "research_ledger": str(output_dir / "research_ledger.json"),
            "run_log": str(output_dir / "run_log.json"),
        },
        path=summary_path,
    )
    artifacts["summary"] = str(summary_path)

    ledger.record_step("validate", "Run deterministic schema, range, missing-value, metric, and claim checks.")
    ledger.record_step("report", "Write report from artifacts only.")
    ledger.outputs = artifacts
    ledger.validation_results = validation_payload
    ledger.validation_summary = validation_summary
    ledger.metrics = metrics_payload
    ledger.report_claims = report_claims
    ledger.warnings = [result.to_dict() for result in validation_results if result.status == "warn"]
    ledger.variable_roles = variable_roles
    ledger.synthetic_truth = synthetic_truth
    ledger.split_metadata = metrics_payload["split_metadata"]
    ledger.write(output_dir / "research_ledger.json")
    artifacts["research_ledger"] = str(output_dir / "research_ledger.json")

    run_log = {
        "project_name": config.project_name,
        "offline": config.offline,
        "output_dir": str(output_dir),
        "elapsed_seconds": round(time.time() - start, 3),
        "hard_failures": [result.to_dict() for result in validation_results if result.status == "fail"],
        "split_metadata": metrics_payload["split_metadata"],
    }
    write_json(output_dir / "run_log.json", run_log)
    artifacts["run_log"] = str(output_dir / "run_log.json")

    benchmark = evaluate_run(output_dir, metrics_payload, validation_results)
    metrics_payload["benchmark"] = benchmark
    write_benchmark_summary(output_dir, benchmark)
    artifacts["benchmark_summary"] = str(output_dir / "benchmark_summary.json")
    write_json(output_dir / "metrics.json", metrics_payload)

    # Refresh ledger after final metrics/run_log writes.
    ledger.outputs = artifacts
    ledger.metrics = metrics_payload
    ledger.warnings = [result.to_dict() for result in validation_results if result.status == "warn"]
    ledger.variable_roles = variable_roles
    ledger.synthetic_truth = synthetic_truth
    ledger.split_metadata = metrics_payload["split_metadata"]
    ledger.write(output_dir / "research_ledger.json")

    return WorkflowResult(output_dir=Path(output_dir), validation_results=validation_results, metrics=metrics_payload, artifacts=artifacts)
