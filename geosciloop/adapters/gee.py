from __future__ import annotations

from typing import Any

from geosciloop.adapters.provenance import DataSourceProvenance


class OptionalDependencyNotAvailable(RuntimeError):
    """Raised when earthengine-api is required but unavailable."""


class GEEAdapter:
    def __init__(self, ee_module: Any | None = None):
        self.ee = ee_module

    def _ee(self) -> Any:
        if self.ee is not None:
            return self.ee
        try:
            import ee
        except ImportError as exc:
            raise OptionalDependencyNotAvailable(
                "Google Earth Engine access requires optional dependency 'earthengine-api' and user authentication."
            ) from exc
        self.ee = ee
        return self.ee

    def initialize(self, project: str | None = None) -> None:
        ee = self._ee()
        if project:
            ee.Initialize(project=project)
        else:
            ee.Initialize()

    def describe_image_collection(
        self,
        collection_id: str,
        bands: list[str],
        start_date: str,
        end_date: str,
        region: dict[str, Any],
    ) -> DataSourceProvenance:
        return DataSourceProvenance(
            provider="Google Earth Engine",
            dataset=collection_id,
            source_type="imagery",
            query={
                "collection_id": collection_id,
                "bands": bands,
                "start_date": start_date,
                "end_date": end_date,
                "region": region,
            },
            temporal_extent={"start_date": start_date, "end_date": end_date},
            spatial_extent={"region": region},
            credentials_required=True,
            access_method="gee_stub",
            notes=[
                "This record describes a requested Earth Engine collection but does not authenticate or download data.",
                "Credentials must be configured outside GeoSciLoop; secrets are never stored in manifests.",
            ],
        )

    def image_collection(self, collection_id: str) -> Any:
        ee = self._ee()
        return ee.ImageCollection(collection_id)
