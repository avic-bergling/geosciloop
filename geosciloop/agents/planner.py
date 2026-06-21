from __future__ import annotations

from pathlib import Path
from typing import Any

from geosciloop.core.artifact_store import write_yaml
from geosciloop.core.schema import TaskConfig


def build_research_plan(config: TaskConfig) -> dict[str, Any]:
    hypotheses = [
        "NDVI is negatively associated with synthetic land surface temperature.",
        "NDBI and building density are positively associated with synthetic land surface temperature.",
        "NDWI is negatively associated with synthetic land surface temperature in this offline demo.",
    ]
    return {
        "project_name": config.project_name,
        "research_question": config.research_question,
        "task_type": config.task_type,
        "aoi": {"name": config.aoi_name, "spatial_unit": f"{config.grid_size_m} m synthetic grid cell"},
        "time_range": {"start_date": config.start_date, "end_date": config.end_date},
        "target_variable": config.target_variable,
        "explanatory_variables": config.explanatory_variables,
        "hypotheses": hypotheses,
        "data_sources": ["deterministic synthetic tabular grid data"],
        "preprocessing": ["generate synthetic grid", "validate ranges", "split deterministic train/test"],
        "modeling": config.models,
        "diagnostics": ["R2", "RMSE", "MAE", "coefficient direction", "feature importance"],
        "outputs": ["data manifest", "metrics", "figures", "research ledger", "Markdown report"],
        "limitations": [
            "Synthetic data are not evidence about a real city.",
            "Associations are not causal effects.",
            "LST is not the same as air temperature.",
        ],
    }


def write_research_plan(config: TaskConfig, path: Path) -> dict[str, Any]:
    plan = build_research_plan(config)
    write_yaml(path, plan)
    return plan
