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
    if {"building_height", "floor_area_ratio", "functional_zone", "population_exposure"}.intersection(config.explanatory_variables):
        hypotheses.extend(
            [
                "Floor area ratio is hypothesized to be positively associated with synthetic land surface temperature.",
                "Building height is treated as a mixed 3D morphology variable rather than a simple directional heat driver.",
                "Functional zones are hypothesized to encode contextual differences in synthetic land surface temperature.",
                "Population exposure is treated as a heat-risk relevance indicator, not as evidence that population causes LST.",
            ]
        )
    return {
        "project_name": config.project_name,
        "research_question": config.research_question,
        "task_type": config.task_type,
        "aoi": {"name": config.aoi_name, "spatial_unit": f"{config.grid_size_m} m synthetic grid cell"},
        "time_range": {"start_date": config.start_date, "end_date": config.end_date},
        "target_variable": config.target_variable,
        "explanatory_variables": config.explanatory_variables,
        "variable_roles": config.variable_roles(),
        "hypotheses": hypotheses,
        "data_sources": ["deterministic synthetic tabular grid data"],
        "preprocessing": ["generate synthetic grid", "validate ranges", "split deterministic train/test"],
        "modeling": config.models,
        "diagnostics": ["R2", "RMSE", "MAE", "coefficient direction", "feature importance"],
        "outputs": ["data manifest", "metrics", "figures", "research ledger", "Markdown report", "human-readable summary"],
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
