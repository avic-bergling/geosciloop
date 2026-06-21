# Metadata Validators

GeoSciLoop v0.2 adds deterministic metadata validators for fixture-based real-data workflow planning. They operate on `data_source_manifest.json` and emit existing pass/warn/fail `ValidationResult` records.

## Validators

- `crs_metadata`: checks CRS presence, mixed raster CRS, and projected target CRS planning.
- `raster_resolution_metadata`: checks raster-like source resolution metadata and resampling plan.
- `raster_alignment_metadata`: checks target CRS, target resolution, and alignment strategy for multiple raster-like sources.
- `nodata_metadata`: checks NoData metadata and NoData handling plan.
- `cloud_shadow_qa_metadata`: checks cloud cover, cloud/shadow QA metadata, cloud thresholds, and handling plan for satellite sources.
- `source_provenance`: checks provider, collection or dataset, datetime, license, query, href, and provenance.
- `split_strategy`: warns when random non-spatial splitting is planned for a geospatial AOI.

## Expected v0.2 Template Warning

`configs/uhi_real_pilot_template.yaml` intentionally uses:

```yaml
split_strategy:
  method: random
  spatial_awareness: false
```

The validator should warn about spatial leakage. This warning is expected and documents why real geospatial modeling should use spatial or block splits.

## Scope Limits

These validators inspect metadata completeness. They do not inspect real raster pixels, vector geometries, cloud masks, or population grid values because the v0.2 prototype does not download or process live data.
