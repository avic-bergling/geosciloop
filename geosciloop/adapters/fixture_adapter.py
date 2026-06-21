from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from geosciloop.adapters.base import AdapterPlan, FetchResult
from geosciloop.core.schema import DataSourceRecord, DataSourceRequest


DEFAULT_FIXTURE_DIR = Path("tests/fixtures")


def load_fixture(fixture_dir: Path | str, fixture_name: str) -> dict[str, Any]:
    path = Path(fixture_dir) / fixture_name
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Fixture must be a JSON object: {path}")
    return payload


def record_from_fixture(payload: dict[str, Any], request: DataSourceRequest | None = None) -> DataSourceRecord:
    role = str(payload.get("role", request.role if request else ""))
    return DataSourceRecord(
        role=role,
        adapter=str(payload.get("adapter", request.adapter if request else "")),
        provider=str(payload.get("provider", request.provider if request else "")),
        collection=str(payload.get("collection", request.collection if request else "")),
        dataset=str(payload.get("dataset", request.dataset if request else "")),
        asset=str(payload.get("asset", "")),
        datetime=str(payload.get("datetime", "")),
        bbox=list(payload.get("bbox", [])),
        crs=payload.get("crs"),
        resolution_m=payload.get("resolution_m"),
        nodata=payload.get("nodata"),
        cloud_cover=payload.get("cloud_cover"),
        cloud_shadow_metadata=dict(payload.get("cloud_shadow_metadata", {})),
        license=str(payload.get("license", request.license if request else "")),
        href=str(payload.get("href", "")),
        downloaded=bool(payload.get("downloaded", False)),
        requires_credentials=bool(payload.get("requires_credentials", False)),
        query=dict(payload.get("query", {})),
        provenance=dict(payload.get("provenance", {})),
        validation_notes=list(payload.get("validation_notes", [])),
    )


class FixtureJsonAdapter:
    def __init__(self, fixture_dir: Path | str = DEFAULT_FIXTURE_DIR):
        self.fixture_dir = Path(fixture_dir)

    def fixture_name_for_request(self, request: DataSourceRequest) -> str:
        raise NotImplementedError

    def plan(self, request: DataSourceRequest) -> AdapterPlan:
        fixture_name = self.fixture_name_for_request(request)
        return AdapterPlan(
            role=request.role,
            adapter=request.adapter,
            provider=request.provider,
            collection=request.collection,
            dataset=request.dataset,
            query_type=request.query_type,
            dry_run=True,
            download=False,
            requires_credentials=False,
            fixture=fixture_name,
            notes=[
                "Fixture-backed dry-run plan. No live request, authentication, or download is performed.",
                request.notes,
            ],
            query={
                "role": request.role,
                "collection": request.collection,
                "dataset": request.dataset,
                "required_metadata": list(request.required_metadata),
            },
        )

    def search(self, request: DataSourceRequest) -> list[dict[str, Any]]:
        return [load_fixture(self.fixture_dir, self.fixture_name_for_request(request))]

    def describe(self, item: dict[str, Any], request: DataSourceRequest | None = None) -> DataSourceRecord:
        return record_from_fixture(item, request=request)

    def fetch(
        self,
        item: dict[str, Any],
        request: DataSourceRequest | None = None,
        dry_run: bool = True,
        output_dir: Path | None = None,
    ) -> FetchResult:
        record = self.describe(item, request=request)
        return FetchResult(
            record=record,
            downloaded=False,
            local_path="",
            notes=["Dry-run fetch skipped. Fixture metadata was described but no data were downloaded."],
        )


class FixturePopulationAdapter(FixtureJsonAdapter):
    def fixture_name_for_request(self, request: DataSourceRequest) -> str:
        return "population_grid_manifest.json"
