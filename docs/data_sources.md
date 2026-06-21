# Data Sources

This document lists candidate real-data sources for future GeoSciLoop workflows. They are not used by the default v0.1 offline demo.

## Remote-Sensing Imagery

- STAC catalogs: candidate interface for Sentinel, Landsat, and other cataloged imagery.
- Google Earth Engine: candidate interface for cloud-hosted image collections.

Required future checks:

- CRS and projection handling.
- Raster alignment and resolution.
- Cloud, shadow, and NoData masks.
- Band scaling and sensor-specific QA fields.
- Clear separation between LST and air temperature.

## Urban Morphology and Built Environment

- OpenStreetMap / Overpass: candidate source for roads and building footprints.
- GHSL-style gridded settlement products: candidate source for built-up and population context.

Required future checks:

- Completeness of volunteered or modeled features.
- Date/version of source snapshots.
- Spatial leakage risk when features are used in ML models.
- Compatibility between vector footprints and raster grids.

## Population and Exposure

- WorldPop-style gridded population data.
- GHSL-style population grids.
- Locally provided exposure rasters or tabular summaries.

Population exposure should be treated as a risk or interpretation layer unless a specific causal or predictive design justifies using it as a model predictor. GeoSciLoop v0.1 synthetic morphology demo keeps `population_exposure` out of default LST predictors.

## Provenance Requirements

For every real-data source, future workflows should record:

- provider and dataset identifier
- access method and query parameters
- spatial extent and time range
- asset URLs or local paths
- version/date of source where available
- credential requirement without storing secrets
- preprocessing and quality caveats

Use `geosciloop.adapters.provenance.build_real_data_manifest` for optional adapter provenance records.
