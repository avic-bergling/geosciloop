from __future__ import annotations

from geosciloop.core.schema import TaskConfig
from geosciloop.core.state import WorkflowResult
from geosciloop.workflows.real_data_dry_run import run_real_data_dry_run
from geosciloop.workflows.urban_heat_island import run_uhi_workflow


def run_config(config: TaskConfig) -> WorkflowResult:
    if config.task_type != "urban_heat_island":
        raise ValueError(f"Unsupported task_type: {config.task_type}")
    if config.mode == "dry_run" or config.dry_run:
        return run_real_data_dry_run(config)
    if not config.offline:
        raise ValueError("GeoSciLoop v0.1 demo must run with offline=true")
    return run_uhi_workflow(config)
