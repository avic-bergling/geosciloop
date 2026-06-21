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
class AOI:
    name: str
    bbox: list[float]
    crs: str


@dataclass
class TimeRange:
    start: str
    end: str


@dataclass
class DataSourceRequest:
    role: str
    adapter: str
    provider: str
    collection: str = ""
    dataset: str = ""
    asset_roles: list[str] = field(default_factory=list)
    query_type: str = "fixture"
    required_tags: list[str] = field(default_factory=list)
    cloud_cover_max: float | None = None
    required_metadata: list[str] = field(default_factory=list)
    license: str = ""
    notes: str = ""


@dataclass
class DataSourceRecord:
    role: str
    adapter: str
    provider: str
    collection: str = ""
    dataset: str = ""
    asset: str = ""
    datetime: str = ""
    bbox: list[float] = field(default_factory=list)
    crs: str | None = None
    resolution_m: float | None = None
    nodata: Any | None = None
    cloud_cover: float | None = None
    cloud_shadow_metadata: dict[str, Any] = field(default_factory=dict)
    license: str = ""
    href: str = ""
    downloaded: bool = False
    requires_credentials: bool = False
    query: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    validation_notes: list[str] = field(default_factory=list)


@dataclass
class SplitStrategy:
    method: str
    spatial_awareness: bool
    notes: str = ""


@dataclass
class DataSourceManifest:
    schema_version: str
    project_name: str
    mode: str
    offline: bool
    dry_run: bool
    sources: list[DataSourceRecord]
    split_strategy: SplitStrategy | None = None
    metadata_plan: dict[str, Any] = field(default_factory=dict)


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
    mode: str = "synthetic"
    dry_run: bool = False
    execution: dict[str, Any] = field(default_factory=dict)
    aoi: AOI = field(default_factory=lambda: AOI(name="", bbox=[], crs=""))
    time_range: TimeRange = field(default_factory=lambda: TimeRange(start="", end=""))
    data_sources: list[DataSourceRequest] = field(default_factory=list)
    split_strategy: SplitStrategy = field(
        default_factory=lambda: SplitStrategy(method="random", spatial_awareness=False, notes="")
    )
    metadata_plan: dict[str, Any] = field(default_factory=dict)

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


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    aoi = normalized.get("aoi") if isinstance(normalized.get("aoi"), dict) else {}
    time_range = normalized.get("time_range") if isinstance(normalized.get("time_range"), dict) else {}
    dry_run = bool(normalized.get("dry_run", normalized.get("mode") == "dry_run"))

    if "aoi_name" not in normalized and aoi.get("name"):
        normalized["aoi_name"] = aoi["name"]
    if "start_date" not in normalized and time_range.get("start"):
        normalized["start_date"] = time_range["start"]
    if "end_date" not in normalized and time_range.get("end"):
        normalized["end_date"] = time_range["end"]
    if "target_variable" not in normalized and normalized.get("target"):
        normalized["target_variable"] = normalized["target"]
    if "explanatory_variables" not in normalized:
        variables = [*normalized.get("predictors", []), *normalized.get("risk_indicators", [])]
        if variables:
            normalized["explanatory_variables"] = variables
    if "grid_size_m" not in normalized:
        normalized["grid_size_m"] = int(normalized.get("metadata_plan", {}).get("target_resolution_m", 30))
    if "models" not in normalized:
        normalized["models"] = ["dry_run_metadata_plan"] if dry_run else []
    if "output_dir" not in normalized and normalized.get("project_name"):
        normalized["output_dir"] = f"outputs/{normalized['project_name']}"
    if "random_seed" not in normalized:
        normalized["random_seed"] = 0
    if "offline" not in normalized and dry_run:
        normalized["offline"] = True
    return normalized


def _parse_aoi(payload: dict[str, Any]) -> AOI:
    raw = payload.get("aoi") if isinstance(payload.get("aoi"), dict) else {}
    return AOI(
        name=str(raw.get("name", payload.get("aoi_name", ""))),
        bbox=[float(value) for value in raw.get("bbox", [])],
        crs=str(raw.get("crs", "")),
    )


def _parse_time_range(payload: dict[str, Any]) -> TimeRange:
    raw = payload.get("time_range") if isinstance(payload.get("time_range"), dict) else {}
    return TimeRange(
        start=str(raw.get("start", payload.get("start_date", ""))),
        end=str(raw.get("end", payload.get("end_date", ""))),
    )


def _parse_data_sources(payload: dict[str, Any]) -> list[DataSourceRequest]:
    sources = payload.get("data_sources", [])
    if sources is None:
        return []
    requests: list[DataSourceRequest] = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("data_sources entries must be mappings")
        requests.append(
            DataSourceRequest(
                role=str(source["role"]),
                adapter=str(source["adapter"]),
                provider=str(source["provider"]),
                collection=str(source.get("collection", "")),
                dataset=str(source.get("dataset", "")),
                asset_roles=list(source.get("asset_roles", [])),
                query_type=str(source.get("query_type", "fixture")),
                required_tags=list(source.get("required_tags", [])),
                cloud_cover_max=(
                    float(source["cloud_cover_max"]) if source.get("cloud_cover_max") is not None else None
                ),
                required_metadata=list(source.get("required_metadata", [])),
                license=str(source.get("license", "")),
                notes=str(source.get("notes", "")),
            )
        )
    return requests


def _parse_split_strategy(payload: dict[str, Any]) -> SplitStrategy:
    raw = payload.get("split_strategy") if isinstance(payload.get("split_strategy"), dict) else {}
    return SplitStrategy(
        method=str(raw.get("method", "random")),
        spatial_awareness=bool(raw.get("spatial_awareness", False)),
        notes=str(raw.get("notes", "")),
    )


def parse_task_config(payload: dict[str, Any]) -> TaskConfig:
    payload = _normalize_payload(payload)
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
        mode=str(payload.get("mode", "synthetic")),
        dry_run=bool(payload.get("dry_run", False)),
        execution=dict(payload.get("execution", {})),
        aoi=_parse_aoi(payload),
        time_range=_parse_time_range(payload),
        data_sources=_parse_data_sources(payload),
        split_strategy=_parse_split_strategy(payload),
        metadata_plan=dict(payload.get("metadata_plan", {})),
    )


def load_task_config(
    path: Path | str,
    offline_override: bool | None = None,
    dry_run_override: bool | None = None,
) -> TaskConfig:
    config_path = Path(path)
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    if offline_override is not None:
        payload["offline"] = offline_override
    if dry_run_override is not None:
        payload["dry_run"] = dry_run_override
        if dry_run_override:
            payload["mode"] = "dry_run"
            payload["offline"] = True
    return parse_task_config(payload)
