"""Optional real-data and fixture adapter interfaces for GeoSciLoop."""

from geosciloop.adapters.base import AdapterPlan, FetchResult
from geosciloop.adapters.fixture_adapter import FixturePopulationAdapter
from geosciloop.adapters.gee_adapter import FixtureGEEAdapter
from geosciloop.adapters.osm_adapter import FixtureOSMAdapter
from geosciloop.adapters.provenance import DataSourceProvenance, build_real_data_manifest
from geosciloop.adapters.registry import build_adapter
from geosciloop.adapters.stac_adapter import FixtureSTACAdapter

__all__ = [
    "AdapterPlan",
    "DataSourceProvenance",
    "FetchResult",
    "FixtureGEEAdapter",
    "FixtureOSMAdapter",
    "FixturePopulationAdapter",
    "FixtureSTACAdapter",
    "build_adapter",
    "build_real_data_manifest",
]
