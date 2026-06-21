from __future__ import annotations

from geosciloop.adapters.fixture_adapter import FixtureJsonAdapter
from geosciloop.core.schema import DataSourceRequest


class FixtureSTACAdapter(FixtureJsonAdapter):
    def fixture_name_for_request(self, request: DataSourceRequest) -> str:
        key = (request.collection or request.dataset or request.role).lower()
        if "sentinel" in key or request.role == "optical":
            return "stac_sentinel2_l2a_item.json"
        if "landsat" in key or request.role == "lst":
            return "stac_landsat_l2_item.json"
        raise ValueError(f"No STAC fixture is registered for request: {request.role}/{request.collection}")
