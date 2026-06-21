from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from geosciloop.core.schema import DataSourceRecord, DataSourceRequest


@dataclass
class AdapterPlan:
    role: str
    adapter: str
    provider: str
    collection: str = ""
    dataset: str = ""
    query_type: str = "fixture"
    dry_run: bool = True
    download: bool = False
    requires_credentials: bool = False
    fixture: str = ""
    notes: list[str] = field(default_factory=list)
    query: dict[str, Any] = field(default_factory=dict)


@dataclass
class FetchResult:
    record: DataSourceRecord
    downloaded: bool = False
    local_path: str = ""
    notes: list[str] = field(default_factory=list)


class DataAdapter(Protocol):
    def plan(self, request: DataSourceRequest) -> AdapterPlan:
        ...

    def search(self, request: DataSourceRequest) -> list[dict[str, Any]]:
        ...

    def describe(self, item: dict[str, Any], request: DataSourceRequest | None = None) -> DataSourceRecord:
        ...

    def fetch(
        self,
        item: dict[str, Any],
        request: DataSourceRequest | None = None,
        dry_run: bool = True,
        output_dir: Path | None = None,
    ) -> FetchResult:
        ...
