import importlib.metadata
from pathlib import Path

from geosciloop.adapters.gee import GEEAdapter, OptionalDependencyNotAvailable
from geosciloop.adapters.gee_adapter import FixtureGEEAdapter
from geosciloop.adapters.osm import OSMAdapter
from geosciloop.adapters.osm_adapter import FixtureOSMAdapter
from geosciloop.adapters.provenance import DataSourceProvenance, build_real_data_manifest
from geosciloop.adapters.stac import STACAdapter
from geosciloop.adapters.stac_adapter import FixtureSTACAdapter
from geosciloop.adapters.registry import build_adapter
from geosciloop.core.schema import DataSourceRequest


class FakeSTACSearch:
    def items(self):
        return [
            {
                "id": "scene-1",
                "collection": "landsat-c2-l2",
                "assets": {
                    "red": {"href": "https://example.invalid/red.tif"},
                    "nir": {"href": "https://example.invalid/nir.tif"},
                },
                "properties": {"datetime": "2024-07-15T10:00:00Z"},
            }
        ]


class FakeSTACClient:
    def __init__(self):
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return FakeSTACSearch()


class FakeOverpassClient:
    def __init__(self):
        self.query_text = None

    def query(self, query_text):
        self.query_text = query_text
        return {
            "elements": [
                {"type": "way", "id": 11, "tags": {"highway": "residential"}},
                {"type": "way", "id": 12, "tags": {"building": "yes"}},
            ]
        }


def test_base_install_does_not_require_stac_or_gee_dependencies():
    dependencies = importlib.metadata.requires("geosciloop") or []
    normalized = "\n".join(dependencies).lower()

    assert "pystac" not in normalized
    assert "earthengine" not in normalized
    assert "google-earth-engine" not in normalized


def test_stac_adapter_uses_injected_client_and_builds_provenance_without_network():
    client = FakeSTACClient()
    adapter = STACAdapter(client=client, catalog_url="https://example.invalid/catalog")

    results = adapter.search(
        collections=["landsat-c2-l2"],
        bbox=[-75.0, 40.0, -74.0, 41.0],
        datetime_range="2024-07-01/2024-08-31",
        query={"eo:cloud_cover": {"lt": 20}},
        limit=5,
    )

    assert client.calls == [
        {
            "collections": ["landsat-c2-l2"],
            "bbox": [-75.0, 40.0, -74.0, 41.0],
            "datetime": "2024-07-01/2024-08-31",
            "query": {"eo:cloud_cover": {"lt": 20}},
            "limit": 5,
        }
    ]
    assert results[0].provider == "STAC"
    assert results[0].dataset == "landsat-c2-l2"
    assert results[0].assets[0]["asset_key"] == "red"
    assert results[0].query["catalog_url"] == "https://example.invalid/catalog"


def test_gee_adapter_stub_records_requested_collection_without_credentials():
    adapter = GEEAdapter(ee_module=None)

    record = adapter.describe_image_collection(
        collection_id="LANDSAT/LC08/C02/T1_L2",
        bands=["SR_B4", "SR_B5", "ST_B10"],
        start_date="2024-07-01",
        end_date="2024-08-31",
        region={"type": "Polygon", "coordinates": []},
    )

    assert record.provider == "Google Earth Engine"
    assert record.dataset == "LANDSAT/LC08/C02/T1_L2"
    assert record.credentials_required is True
    assert record.query["bands"] == ["SR_B4", "SR_B5", "ST_B10"]
    assert record.notes


def test_gee_adapter_initialize_requires_optional_dependency_when_missing():
    adapter = GEEAdapter(ee_module=None)

    try:
        adapter.initialize()
    except OptionalDependencyNotAvailable as exc:
        assert "earthengine-api" in str(exc)
    else:
        raise AssertionError("Expected missing Earth Engine dependency to raise")


def test_osm_adapter_uses_injected_overpass_client_and_records_roads_buildings():
    client = FakeOverpassClient()
    adapter = OSMAdapter(overpass_client=client)

    record = adapter.query_roads_and_buildings(bbox=[40.0, -75.0, 41.0, -74.0])

    assert "[highway]" in client.query_text
    assert "[building]" in client.query_text
    assert record.provider == "OpenStreetMap"
    assert record.dataset == "overpass_roads_buildings"
    assert record.assets == [
        {"type": "way", "id": 11, "tags": {"highway": "residential"}},
        {"type": "way", "id": 12, "tags": {"building": "yes"}},
    ]


def test_real_data_manifest_records_provenance_without_secrets():
    records = [
        DataSourceProvenance(
            provider="STAC",
            dataset="sentinel-2-l2a",
            source_type="imagery",
            query={"token": "SECRET", "bbox": [0, 1, 2, 3]},
            assets=[{"href": "https://example.invalid/a.tif"}],
            credentials_required=False,
        ),
        DataSourceProvenance(
            provider="Google Earth Engine",
            dataset="LANDSAT/LC08/C02/T1_L2",
            source_type="imagery",
            query={"service_account_key": "SECRET"},
            credentials_required=True,
        ),
    ]

    manifest = build_real_data_manifest(records, run_mode="real_data_optional")

    assert manifest["run_mode"] == "real_data_optional"
    assert manifest["record_count"] == 2
    assert manifest["records"][0]["query"]["token"] == "<redacted>"
    assert manifest["records"][1]["query"]["service_account_key"] == "<redacted>"
    assert manifest["records"][1]["credentials_required"] is True


def _request(role: str, adapter: str, collection: str = "", dataset: str = "") -> DataSourceRequest:
    return DataSourceRequest(
        role=role,
        adapter=adapter,
        provider="fixture",
        collection=collection,
        dataset=dataset,
        asset_roles=["metadata"],
        query_type="fixture",
        required_tags=[],
        cloud_cover_max=20.0 if role in {"lst", "optical"} else None,
        required_metadata=["crs", "resolution_m", "nodata", "provenance"],
        license="fixture-only",
        notes="test request",
    )


def test_fixture_stac_adapter_returns_landsat_and_sentinel_metadata_without_network():
    fixture_dir = Path("tests/fixtures")
    adapter = FixtureSTACAdapter(fixture_dir=fixture_dir)

    landsat = adapter.describe(adapter.search(_request("lst", "fixture_stac", collection="landsat-c2-l2"))[0])
    sentinel = adapter.describe(adapter.search(_request("optical", "fixture_stac", collection="sentinel-2-l2a"))[0])

    assert landsat.provider == "USGS"
    assert landsat.collection == "landsat-c2-l2"
    assert landsat.role == "lst"
    assert landsat.href.startswith("mock://")
    assert landsat.downloaded is False
    assert landsat.requires_credentials is False
    assert landsat.cloud_shadow_metadata["qa_band"] == "QA_PIXEL"
    assert sentinel.provider == "ESA"
    assert sentinel.collection == "sentinel-2-l2a"
    assert sentinel.role == "optical"
    assert sentinel.cloud_cover == 8.5


def test_fixture_osm_adapter_returns_road_metadata_without_network():
    adapter = FixtureOSMAdapter(fixture_dir=Path("tests/fixtures"))

    record = adapter.describe(adapter.search(_request("roads", "fixture_osm", dataset="osm_roads"))[0])

    assert record.provider == "OpenStreetMap"
    assert record.dataset == "osm_roads"
    assert record.role == "roads"
    assert record.resolution_m is None
    assert record.downloaded is False
    assert record.provenance["fixture"] == "osm_roads_response.json"


def test_registry_builds_fixture_adapters_by_name():
    fixture_dir = Path("tests/fixtures")

    assert isinstance(build_adapter("fixture_stac", fixture_dir=fixture_dir), FixtureSTACAdapter)
    assert isinstance(build_adapter("fixture_osm", fixture_dir=fixture_dir), FixtureOSMAdapter)
    assert isinstance(build_adapter("fixture_gee", fixture_dir=fixture_dir), FixtureGEEAdapter)
