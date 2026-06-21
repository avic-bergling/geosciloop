# Optional Real-Data Adapters

GeoSciLoop keeps the v0.1 synthetic UHI demo fully offline. Real-data access is exposed only through optional adapter modules under `geosciloop.adapters`; the base package does not require STAC, Google Earth Engine, OSM, API keys, or internet access.

## Design Rules

- Offline synthetic workflows and tests remain the default.
- Adapter tests use injected fake clients only.
- Credentials are supplied by the user environment, never hardcoded.
- Manifests redact common secret fields such as `token`, `api_key`, `password`, and `service_account_key`.
- Adapter records are provenance records, not validated scientific evidence.

## STAC

Module: `geosciloop.adapters.stac`

`STACAdapter` supports a STAC search interface and optional asset download helper. It accepts an injected client for tests or, when used for real access, lazily imports `pystac-client`.

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

Install any STAC client dependency explicitly in the environment used for real-data runs. It is not part of the base install.

## Google Earth Engine

Module: `geosciloop.adapters.gee`

`GEEAdapter` can create provenance records without authentication through `describe_image_collection`. Calling `initialize()` or real Earth Engine APIs requires the optional `earthengine-api` package and user authentication configured outside GeoSciLoop.

Do not commit service-account keys, refresh tokens, or private keys. If those values appear in adapter query dictionaries, manifest helpers redact them.

## OpenStreetMap / Overpass

Module: `geosciloop.adapters.osm`

`OSMAdapter` builds an Overpass query for roads and buildings and supports an injected Overpass client. Offline tests use injected clients; real Overpass calls should respect Overpass usage policies and should be cached outside CI.

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

These records can be included in a future `data_manifest.json` for real-data workflows. They are intentionally separate from the synthetic v0.1 manifest so offline CI remains stable.
