from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = [
    "project_name",
    "task_type",
    "research_question",
    "aoi_name",
    "start_date",
    "end_date",
    "target_variable",
    "explanatory_variables",
    "grid_size_m",
    "models",
    "output_dir",
    "random_seed",
    "offline",
]


@dataclass
class TaskConfig:
    project_name: str
    task_type: str
    research_question: str
    aoi_name: str
    start_date: str
    end_date: str
    target_variable: str
    explanatory_variables: list[str]
    grid_size_m: int
    models: list[str]
    output_dir: Path
    random_seed: int
    offline: bool
    target: str = ""
    predictors: list[str] = field(default_factory=list)
    risk_indicators: list[str] = field(default_factory=list)
    categorical_variables: list[str] = field(default_factory=list)
    metadata_variables: list[str] = field(default_factory=lambda: ["cell_id", "x", "y"])
    n_cells: int = 625
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["output_dir"] = str(self.output_dir)
        return payload

    def variable_roles(self) -> dict[str, Any]:
        return {
            "target": self.target or self.target_variable,
            "target_variable": self.target_variable,
            "explanatory_variables": list(self.explanatory_variables),
            "predictors": list(self.predictors),
            "risk_indicators": list(self.risk_indicators),
            "categorical_variables": list(self.categorical_variables),
            "metadata_variables": list(self.metadata_variables),
        }


def parse_task_config(payload: dict[str, Any]) -> TaskConfig:
    missing = [field_name for field_name in REQUIRED_FIELDS if field_name not in payload]
    if missing:
        raise ValueError(f"Missing required config field(s): {', '.join(missing)}")

    explanatory_variables = list(payload["explanatory_variables"])
    models = list(payload["models"])
    predictors = list(payload.get("predictors", explanatory_variables))
    risk_indicators = list(payload.get("risk_indicators", []))
    categorical_variables = list(payload.get("categorical_variables", []))
    metadata_variables = list(payload.get("metadata_variables", ["cell_id", "x", "y"]))
    target = str(payload.get("target", payload["target_variable"]))
    if not explanatory_variables:
        raise ValueError("explanatory_variables must not be empty")
    if not predictors:
        raise ValueError("predictors must not be empty")
    if not models:
        raise ValueError("models must not be empty")
    if int(payload["grid_size_m"]) <= 0:
        raise ValueError("grid_size_m must be positive")
    if int(payload.get("n_cells", 625)) <= 0:
        raise ValueError("n_cells must be positive")

    return TaskConfig(
        project_name=str(payload["project_name"]),
        task_type=str(payload["task_type"]),
        research_question=str(payload["research_question"]),
        aoi_name=str(payload["aoi_name"]),
        start_date=str(payload["start_date"]),
        end_date=str(payload["end_date"]),
        target_variable=str(payload["target_variable"]),
        explanatory_variables=explanatory_variables,
        grid_size_m=int(payload["grid_size_m"]),
        models=models,
        output_dir=Path(payload["output_dir"]),
        random_seed=int(payload["random_seed"]),
        offline=bool(payload["offline"]),
        target=target,
        predictors=predictors,
        risk_indicators=risk_indicators,
        categorical_variables=categorical_variables,
        metadata_variables=metadata_variables,
        n_cells=int(payload.get("n_cells", 625)),
        metadata=dict(payload.get("metadata", {})),
    )


def load_task_config(path: Path | str, offline_override: bool | None = None) -> TaskConfig:
    config_path = Path(path)
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    if offline_override is not None:
        payload["offline"] = offline_override
    return parse_task_config(payload)
