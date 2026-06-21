from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_json
from geosciloop.core.schema import TaskConfig


@dataclass
class ResearchLedger:
    task_config: dict[str, Any]
    generated_hypotheses: list[str] = field(default_factory=list)
    data_manifest: dict[str, Any] = field(default_factory=dict)
    workflow_steps: list[dict[str, Any]] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    validation_summary: dict[str, int] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    report_claims: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    variable_roles: dict[str, Any] = field(default_factory=dict)
    synthetic_truth: dict[str, Any] = field(default_factory=dict)
    split_metadata: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False
    download_performed: bool = False
    credentials_required: bool = False
    aoi: dict[str, Any] = field(default_factory=dict)
    time_range: dict[str, Any] = field(default_factory=dict)
    data_source_requests: list[dict[str, Any]] = field(default_factory=list)
    adapter_plans: list[dict[str, Any]] = field(default_factory=list)
    data_source_manifest: dict[str, Any] = field(default_factory=dict)
    metadata_validation_results: list[dict[str, Any]] = field(default_factory=list)
    metadata_validation_summary: dict[str, int] = field(default_factory=dict)
    benchmark_summary: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    @classmethod
    def from_config(cls, config: TaskConfig) -> "ResearchLedger":
        return cls(task_config=config.to_dict())

    def record_step(self, name: str, description: str) -> None:
        self.workflow_steps.append({"name": name, "description": description})

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_config": self.task_config,
            "generated_hypotheses": self.generated_hypotheses,
            "data_manifest": self.data_manifest,
            "workflow_steps": self.workflow_steps,
            "outputs": self.outputs,
            "validation_results": self.validation_results,
            "validation_summary": self.validation_summary,
            "metrics": self.metrics,
            "report_claims": self.report_claims,
            "warnings": self.warnings,
            "variable_roles": self.variable_roles,
            "synthetic_truth": self.synthetic_truth,
            "split_metadata": self.split_metadata,
            "dry_run": self.dry_run,
            "download_performed": self.download_performed,
            "credentials_required": self.credentials_required,
            "aoi": self.aoi,
            "time_range": self.time_range,
            "data_source_requests": self.data_source_requests,
            "adapter_plans": self.adapter_plans,
            "data_source_manifest": self.data_source_manifest,
            "metadata_validation_results": self.metadata_validation_results,
            "metadata_validation_summary": self.metadata_validation_summary,
            "benchmark_summary": self.benchmark_summary,
            "limitations": self.limitations,
        }

    def write(self, path: Path) -> Path:
        return write_json(path, self.to_dict())
