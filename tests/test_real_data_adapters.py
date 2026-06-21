import importlib.metadata

from geosciloop.adapters.gee import GEEAdapter, OptionalDependencyNotAvailable
from geosciloop.adapters.osm import OSMAdapter
from geosciloop.adapters.provenance import DataSourceProvenance, build_real_data_manifest
from geosciloop.adapters.stac import STACAdapter


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
