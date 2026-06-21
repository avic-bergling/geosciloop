from __future__ import annotations

from geosciloop.adapters.fixture_adapter import FixtureJsonAdapter
from geosciloop.core.schema import DataSourceRequest


class FixtureGEEAdapter(FixtureJsonAdapter):
    def fixture_name_for_request(self, request: DataSourceRequest) -> str:
        return "gee_collection_stub.json"
