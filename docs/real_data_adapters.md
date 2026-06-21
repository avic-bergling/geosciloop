# Real-Data Adapter Prototype

GeoSciLoop keeps the v0.1 synthetic UHI demos fully offline. v0.2 adds a fixture-based real-data adapter prototype for dry-run planning. The base package still does not require STAC, Google Earth Engine, OSM, API keys, credentials, or internet access.

## Design Rules

- Offline synthetic workflows and tests remain the default.
- v0.2 dry-run adapters use local fixtures by default.
- Adapter tests use injected fake clients or local fixtures only.
- Credentials are supplied by the user environment, never hardcoded.
- Manifests redact common secret fields such as `token`, `api_key`, `password`, and `service_account_key`.
- Adapter records are provenance records, not validated scientific evidence.
- Provider-backed access is future work unless explicitly configured outside required tests.

## v0.2 Fixture Interface

The v0.2 adapter interface is:

- `plan(request)`: returns an adapter plan with dry-run and fixture metadata.
- `search(request)`: returns fixture items.
- `describe(item, request)`: converts fixture metadata to a data source record.
- `fetch(item, request, dry_run=True)`: records that no download was performed.

Implemented fixture adapters:

- `FixtureSTACAdapter` for Landsat and Sentinel fixture items.
- `FixtureGEEAdapter` for a dry-run Earth Engine collection stub.
- `FixtureOSMAdapter` for an Overpass-like roads fixture.
- `FixturePopulationAdapter` for population-grid manifest metadata.

## STAC

Module: `geosciloop.adapters.stac`

`FixtureSTACAdapter` is the v0.2 default for dry-run planning. The older `STACAdapter` supports a STAC search interface and optional asset download helper, but it is not used by required tests.

Example:

```python
from geosciloop.adapters.stac import STACAdapter

adapter = STACAdapter("https://example-stac/catalog.json")
records = adapter.search(
    collections=["sentinel-2-l2a"],
    bbox=[-75.0, 40.0, -74.0, 41.0],
    datetime_range="2024-07-01/2024-08-31",
    query={"eo:cloud_cover": {"lt": 20}},
    limit=10,
)
```

Install any STAC client dependency explicitly in the environment used for future live real-data runs. It is not part of the base install.

## Google Earth Engine

Module: `geosciloop.adapters.gee`

`GEEAdapter` can create provenance records without authentication through `describe_image_collection`. Calling `initialize()` or real Earth Engine APIs requires the optional `earthengine-api` package and user authentication configured outside GeoSciLoop.

`FixtureGEEAdapter` is dry-run only and reads `tests/fixtures/gee_collection_stub.json`.

Do not commit service-account keys, refresh tokens, or private keys. If those values appear in adapter query dictionaries, manifest helpers redact them.

## OpenStreetMap / Overpass

Module: `geosciloop.adapters.osm`

`OSMAdapter` builds an Overpass query for roads and buildings and supports an injected Overpass client. Offline tests use injected clients; real Overpass calls should respect Overpass usage policies and should be cached outside CI.

`FixtureOSMAdapter` reads `tests/fixtures/osm_roads_response.json` and does not call Overpass.

OSM data are volunteered geographic information. Completeness varies by place and must be checked before scientific interpretation.

## Provenance Manifest

Module: `geosciloop.adapters.provenance`

Use `DataSourceProvenance` and `build_real_data_manifest` to record source metadata:

- provider
- dataset
- source type
- query parameters
- assets
- spatial and temporal extent
- whether credentials are required
- access method
- notes and caveats

v0.2 writes `data_source_manifest.json` for dry-run planning. These records are intentionally separate from the synthetic v0.1 `data_manifest.json` so offline CI remains stable.
