from __future__ import annotations

from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_text
from geosciloop.core.schema import TaskConfig


def _summary_counts(validation_report: dict[str, Any]) -> str:
    summary = validation_report.get("summary", {})
    return (
        f"pass={summary.get('pass', 0)}, "
        f"warn={summary.get('warn', 0)}, "
        f"fail={summary.get('fail', 0)}"
    )


def _warning_lines(validation_report: dict[str, Any]) -> list[str]:
    warnings = [
        result["message"]
        for result in validation_report.get("results", [])
        if result.get("status") == "warn"
    ]
    return [f"- {message}" for message in warnings] or ["- No warnings were emitted."]


def build_dry_run_report(
    config: TaskConfig,
    adapter_plan: dict[str, Any],
    data_source_manifest: dict[str, Any],
    validation_report: dict[str, Any],
) -> str:
    source_lines = []
    for source in data_source_manifest.get("sources", []):
        collection_or_dataset = source.get("collection") or source.get("dataset")
        source_lines.append(
            f"- `{source['role']}` via `{source['adapter']}`: {source['provider']} "
            f"`{collection_or_dataset}`; href `{source['href']}`; downloaded={source['downloaded']}."
        )

    required_metadata = sorted(
        {
            metadata
            for request in config.data_sources
            for metadata in request.required_metadata
        }
    )
    lines = [
        f"# Dry-Run Real-Data Planning Report: {config.project_name}",
        "",
        "## Research question",
        "",
        config.research_question,
        "",
        "## Dry-run disclaimer",
        "",
        "This is a fixture-backed dry-run. No data were downloaded, no provider was contacted, and no credentials were used.",
        "The output is not a real-world UHI conclusion and is not evidence about any real city.",
        "",
        "## Planned AOI and time range",
        "",
        f"- AOI: {config.aoi.name}",
        f"- BBox: {config.aoi.bbox}",
        f"- AOI CRS: {config.aoi.crs}",
        f"- Time range: {config.time_range.start} to {config.time_range.end}",
        "",
        "## Planned data sources",
        "",
        *source_lines,
        "",
        "## Source roles",
        "",
        f"- Target variable: `{config.target_variable}`",
        f"- Predictors: {', '.join(config.predictors)}",
        f"- Risk indicators: {', '.join(config.risk_indicators) or 'none'}",
        "",
        "## Required metadata",
        "",
        *(f"- `{metadata}`" for metadata in required_metadata),
        "",
        "## Metadata validation summary",
        "",
        f"- {_summary_counts(validation_report)}",
        f"- Full records: `metadata_validation_report.json`",
        "",
        "## Warnings",
        "",
        *_warning_lines(validation_report),
        "",
        "## What would be needed for a live run",
        "",
        "- Explicit provider configuration outside the required offline tests.",
        "- User-managed credentials where a provider requires them.",
        "- Real raster/vector downloads or exports into a documented local artifact store.",
        "- Product-specific cloud, shadow, scaling, NoData, CRS, and alignment checks.",
        "- Spatial or block split strategy before model evaluation.",
        "",
        "## Limitations",
        "",
        "- Fixture metadata is representative planning data, not authoritative provider metadata.",
        "- No raster pixels, vector geometries, or population grid values were processed.",
        "- Metadata validators check planning completeness, not real data quality.",
        "- LST is land surface temperature, not air temperature.",
        "- No causal or real-world scientific claim is made.",
        "",
        "## Next steps",
        "",
        "- Review `data_source_manifest.json` and `metadata_validation_report.json`.",
        "- Replace fixture adapters with explicit provider-backed adapters only after preserving offline tests.",
        "- Add spatial/block split design before using real geospatial data for model evaluation.",
    ]
    if adapter_plan.get("plans"):
        lines.extend(["", "## Adapter plans", ""])
        lines.extend(
            f"- `{plan['role']}` planned through `{plan['adapter']}` using fixture `{plan.get('fixture', '')}`."
            for plan in adapter_plan["plans"]
        )
    return "\n".join(lines) + "\n"


def build_dry_run_summary(
    config: TaskConfig,
    data_source_manifest: dict[str, Any],
    validation_report: dict[str, Any],
    benchmark_summary: dict[str, Any] | None,
    artifacts: dict[str, str],
) -> str:
    failures = validation_report.get("summary", {}).get("fail", 0)
    status = "Run succeeded" if failures == 0 else "Run failed validation"
    source_roles = ", ".join(source["role"] for source in data_source_manifest.get("sources", []))
    warning_lines = _warning_lines(validation_report)
    benchmark_line = "pending" if benchmark_summary is None else benchmark_summary.get("schema_version", "available")
    lines = [
        f"# GeoSciLoop Dry-Run Summary: {config.project_name}",
        "",
        "This page summarizes a fixture-based real-data planning dry-run. The JSON artifacts remain the source of truth.",
        "",
        "## 1. What was run",
        "",
        f"- Project: `{config.project_name}`",
        f"- Mode: `{config.mode}`",
        f"- Offline: {config.offline}",
        f"- Dry-run: {config.dry_run}",
        f"- Research question: {config.research_question}",
        f"- Planned AOI: {config.aoi.name} ({config.aoi.crs})",
        f"- Planned time range: {config.time_range.start} to {config.time_range.end}",
        "",
        "## 2. Run status",
        "",
        f"- {status}.",
        f"- Hard validation failures: {failures}",
        "- No data were downloaded.",
        "- No credentials were required.",
        "",
        "## 3. Planned data sources",
        "",
        f"- Source roles: {source_roles}",
        *(
            f"- `{source['role']}`: {source['provider']} `{source.get('collection') or source.get('dataset')}`"
            for source in data_source_manifest.get("sources", [])
        ),
        "",
        "## 4. Validator outcomes",
        "",
        f"- Pass: {validation_report.get('summary', {}).get('pass', 0)}",
        f"- Warn: {validation_report.get('summary', {}).get('warn', 0)}",
        f"- Fail: {validation_report.get('summary', {}).get('fail', 0)}",
        "- Warnings mark planning caveats that must be handled before live real-data analysis.",
        *warning_lines,
        "",
        "## 5. Files for humans",
        "",
        "- `summary.md`",
        "- `dry_run_report.md`",
        "",
        "## 6. Files for developers and auditors",
        "",
        "- `adapter_plan.json`",
        "- `data_source_manifest.json`",
        "- `metadata_validation_report.json`",
        "- `research_ledger.json`",
        "- `benchmark_summary.json`",
        "- `run_log.json`",
        "",
        "## 7. Benchmark",
        "",
        f"- Benchmark summary: {benchmark_line}",
        "",
        "## 8. Next step",
        "",
        "- Review warnings, especially spatial split leakage, before any provider-backed run.",
        "- Keep provider-backed access outside required offline tests unless explicitly configured.",
        "- This dry-run makes no real-world scientific claims.",
        "",
        "## 9. Artifact map",
        "",
    ]
    lines.extend(f"- `{name}`: `{path}`" for name, path in artifacts.items())
    return "\n".join(lines) + "\n"


def write_dry_run_report(
    config: TaskConfig,
    adapter_plan: dict[str, Any],
    data_source_manifest: dict[str, Any],
    validation_report: dict[str, Any],
    path: Path,
) -> str:
    report = build_dry_run_report(config, adapter_plan, data_source_manifest, validation_report)
    write_text(path, report)
    return report


def write_dry_run_summary(
    config: TaskConfig,
    data_source_manifest: dict[str, Any],
    validation_report: dict[str, Any],
    benchmark_summary: dict[str, Any] | None,
    artifacts: dict[str, str],
    path: Path,
) -> str:
    summary = build_dry_run_summary(config, data_source_manifest, validation_report, benchmark_summary, artifacts)
    write_text(path, summary)
    return summary
