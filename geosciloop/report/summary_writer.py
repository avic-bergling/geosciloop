from __future__ import annotations

from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_text
from geosciloop.core.schema import TaskConfig


def _fmt(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return "not available"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}"


def _artifact_name(path_or_name: str) -> str:
    return Path(path_or_name).name


def _dedupe_lines(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _ensure_limitations(limitations: list[str]) -> list[str]:
    normalized = [item.casefold() for item in limitations]
    additions = []
    if not any("lst" in item and "air temperature" in item for item in normalized):
        additions.append("LST is land surface temperature, not air temperature.")
    if not any("causal" in item for item in normalized):
        additions.append("Associations are not causal effects.")
    return _dedupe_lines([*limitations, *additions])


def build_summary_markdown(
    config: TaskConfig,
    data_manifest: dict[str, Any],
    metrics: dict[str, Any],
    validation_report: dict[str, Any],
    report_claims: list[dict[str, Any]],
    critic_summary: dict[str, Any],
    artifacts: dict[str, str],
) -> str:
    failures = validation_report["summary"].get("fail", 0)
    run_status = "Run succeeded" if failures == 0 else "Run failed validation"
    models = metrics.get("models", {})
    linear = models.get("linear_regression", {})
    random_forest = models.get("random_forest", {})
    warnings = validation_report["summary"].get("warn", 0)
    variable_roles = config.variable_roles()
    warning_messages = [
        result["message"]
        for result in validation_report.get("results", [])
        if result.get("status") == "warn"
    ]

    lines = [
        f"# GeoSciLoop Output Summary: {config.project_name}",
        "",
        "This page is a human-readable index for the output directory. The JSON and YAML files remain the machine-readable source of truth.",
        "",
        "## 1. What was run",
        "",
        f"- Project: `{config.project_name}`",
        f"- Task type: `{config.task_type}`",
        f"- Research question: {config.research_question}",
        f"- AOI: {config.aoi_name}",
        f"- Offline mode: {config.offline}",
        f"- Target: `{variable_roles['target']}`",
        f"- Predictors used for LST modeling: {', '.join(variable_roles['predictors'])}",
        f"- Risk indicators: {', '.join(variable_roles['risk_indicators']) or 'none'}",
        "",
        "## 2. Run status",
        "",
        f"- {run_status}.",
        f"- Hard validation failures: {failures}",
        f"- See `{_artifact_name(artifacts['validation_report'])}` and `{_artifact_name(artifacts['run_log'])}` for details.",
        "",
        "## 3. Data used",
        "",
        f"- Data source: {data_manifest.get('source', 'deterministic synthetic data')}.",
        f"- Rows: {data_manifest.get('n_rows')}",
        f"- Random seed: {data_manifest.get('random_seed')}",
        f"- Data table: `{_artifact_name(artifacts['synthetic_data'])}` in `tables/`.",
        "- This output is not evidence about a real city.",
        "",
        "## 4. Models fitted",
        "",
    ]
    for model_name in models:
        lines.append(f"- `{model_name}`")
    for feature, encoding in metrics.get("feature_encoding", {}).items():
        lines.append(f"- `{feature}` was encoded with `{encoding.get('method', 'documented encoding')}` for modeling.")

    lines.extend(
        [
            "",
            "## 5. Main results",
            "",
            "- Main findings are synthetic, artifact-grounded associations from this offline demo.",
        ]
    )
    if linear:
        lines.extend(
            [
                f"- Linear regression R2: {_fmt(linear.get('r2'))}",
                f"- Linear regression RMSE: {_fmt(linear.get('rmse'))}",
                f"- Linear regression MAE: {_fmt(linear.get('mae'))}",
            ]
        )
    if random_forest:
        lines.extend(
            [
                f"- Random forest R2: {_fmt(random_forest.get('r2'))}",
                f"- Random forest RMSE: {_fmt(random_forest.get('rmse'))}",
                f"- Random forest MAE: {_fmt(random_forest.get('mae'))}",
            ]
        )
    lines.extend(
        [
            f"- Full model details are in `{_artifact_name(artifacts['metrics'])}`.",
            f"- Useful human figures are in `figures/`.",
            "",
            "## 6. Validator outcomes",
            "",
            f"- Pass: {validation_report['summary'].get('pass', 0)}",
            f"- Warn: {warnings}",
            f"- Fail: {validation_report['summary'].get('fail', 0)}",
            f"- Full pass/warn/fail records are in `{_artifact_name(artifacts['validation_report'])}`.",
            "- What warnings mean: the run can still complete, but the warning text marks an interpretation caveat that should be reviewed before trusting claims.",
        ]
    )
    lines.extend(f"- Warning detail: {message}" for message in warning_messages)
    lines.extend(["", "## 7. Supported report claims", ""])
    for claim in report_claims:
        support = claim.get("support_status", "unknown")
        artifact_list = ", ".join(f"`{artifact}`" for artifact in claim.get("supporting_artifacts", []))
        lines.append(f"- {claim['claim']} Status: `{support}`. Supported by: {artifact_list}.")
    lines.extend(
        [
            f"- The complete evidence chain is in `{_artifact_name(artifacts['research_ledger'])}`.",
            "",
            "## 8. Limitations",
            "",
        ]
    )
    limitations = _ensure_limitations(critic_summary.get("limitations", []))
    lines.extend(f"- {limitation}" for limitation in limitations)
    lines.extend(
        [
            "",
            "## 9. What to do next",
            "",
            "- Open `report.md` for the full narrative report.",
            "- Open `figures/` to inspect model and UHI diagnostic plots.",
            "- Human-readable files: `summary.md`, `report.md`, and files under `figures/`.",
            "- Developer/audit files: `data_manifest.json`, `metrics.json`, `validation_report.json`, `research_ledger.json`, `research_plan.yaml`, `synthetic_truth.json`, and `run_log.json`.",
            "- Review `validation_report.json` before trusting any claim.",
            "- Review `research_ledger.json` to trace claims back to metrics, validations, and artifacts.",
            "- For future work, add optional real-data adapters only after preserving the offline test baseline.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_summary(
    config: TaskConfig,
    data_manifest: dict[str, Any],
    metrics: dict[str, Any],
    validation_report: dict[str, Any],
    report_claims: list[dict[str, Any]],
    critic_summary: dict[str, Any],
    artifacts: dict[str, str],
    path: Path,
) -> str:
    summary = build_summary_markdown(
        config=config,
        data_manifest=data_manifest,
        metrics=metrics,
        validation_report=validation_report,
        report_claims=report_claims,
        critic_summary=critic_summary,
        artifacts=artifacts,
    )
    write_text(path, summary)
    return summary
