from __future__ import annotations

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import WorkflowResult
from geosciloop.workflows.urban_heat_island import run_uhi_workflow


def run_config(config: TaskConfig) -> WorkflowResult:
    if config.task_type != "urban_heat_island":
        raise ValueError(f"Unsupported task_type for v0.1: {config.task_type}")
    if not config.offline:
        raise ValueError("GeoSciLoop v0.1 demo must run with offline=true")
    return run_uhi_workflow(config)
