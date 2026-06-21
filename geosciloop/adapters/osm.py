from __future__ import annotations

from typing import Any

from geosciloop.adapters.provenance import DataSourceProvenance


class OSMAdapter:
    def __init__(self, overpass_client: Any | None = None):
        self.overpass_client = overpass_client

    @staticmethod
    def build_roads_buildings_query(bbox: list[float]) -> str:
        south, west, north, east = bbox
        return f"""
[out:json][timeout:25];
(
  way[highway]({south},{west},{north},{east});
  way[building]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
""".strip()

    def query_roads_and_buildings(self, bbox: list[float]) -> DataSourceProvenance:
        query_text = self.build_roads_buildings_query(bbox)
        elements: list[dict[str, Any]] = []
        if self.overpass_client is not None:
            response = self.overpass_client.query(query_text)
            elements = list(response.get("elements", []))
        return DataSourceProvenance(
            provider="OpenStreetMap",
            dataset="overpass_roads_buildings",
            source_type="vector",
            query={"bbox": bbox, "overpass_query": query_text},
            assets=elements,
            spatial_extent={"bbox": bbox},
            credentials_required=False,
            access_method="overpass_query",
            notes=[
                "OSM data are volunteered geographic information and require completeness checks before scientific use.",
                "Offline tests use injected clients and do not call Overpass.",
            ],
        )
