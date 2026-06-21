from geosciloop.core.schema import DataSourceManifest, DataSourceRecord, SplitStrategy
from geosciloop.validators.metadata import run_metadata_validators


def _record(
    role: str,
    *,
    crs: str | None = "EPSG:4326",
    resolution_m: float | None = 30.0,
    nodata: int | None = -9999,
    cloud_cover: float | None = 10.0,
    qa: dict | None = None,
) -> DataSourceRecord:
    return DataSourceRecord(
        role=role,
        adapter="fixture_stac",
        provider="USGS",
        collection="landsat-c2-l2",
        dataset="landsat_l2",
        asset="ST_B10",
        datetime="2024-07-15T10:00:00Z",
        bbox=[-75.25, 39.85, -74.75, 40.25],
        crs=crs,
        resolution_m=resolution_m,
        nodata=nodata,
        cloud_cover=cloud_cover,
        cloud_shadow_metadata=qa or {"qa_band": "QA_PIXEL", "cloud_bit": 3, "shadow_bit": 4},
        license="USGS public domain",
        href="mock://landsat/l2/ST_B10.tif",
        downloaded=False,
        requires_credentials=False,
        query={"bbox": [-75.25, 39.85, -74.75, 40.25]},
        provenance={"fixture": "stac_landsat_l2_item.json"},
        validation_notes=[],
    )


def _manifest(**overrides) -> DataSourceManifest:
    payload = {
        "schema_version": "geosciloop-data-source-manifest-v0.2",
        "project_name": "uhi_real_pilot_template",
        "mode": "dry_run",
        "offline": True,
        "dry_run": True,
        "sources": [_record("lst"), _record("optical", resolution_m=10.0)],
        "split_strategy": SplitStrategy(
            method="random",
            spatial_awareness=False,
            notes="Template intentionally warns about spatial leakage.",
        ),
        "metadata_plan": {
            "target_crs": "EPSG:32618",
            "target_resolution_m": 30,
            "alignment_strategy": "resample all rasters to a 30 m projected grid",
            "nodata_handling": "mask NoData before feature aggregation",
            "cloud_shadow_handling": "apply provider QA bands before analysis",
        },
    }
    payload.update(overrides)
    return DataSourceManifest(**payload)


def test_metadata_validators_pass_when_required_metadata_is_present():
    results = run_metadata_validators(_manifest())

    assert any(result.name == "crs_metadata" and result.status == "pass" for result in results)
    assert any(result.name == "raster_alignment_metadata" and result.status == "pass" for result in results)
    assert any(result.name == "nodata_metadata" and result.status == "pass" for result in results)
    assert any(result.name == "source_provenance" and result.status == "pass" for result in results)


def test_metadata_validators_warn_for_missing_crs_and_nodata_plan():
    manifest = _manifest(
        sources=[_record("lst", crs=None, nodata=None)],
        metadata_plan={"target_crs": "", "alignment_strategy": "", "nodata_handling": ""},
    )

    results = run_metadata_validators(manifest)

    assert any(result.name == "crs_metadata" and result.status == "warn" and "missing" in result.message.lower() for result in results)
    assert any(result.name == "nodata_metadata" and result.status == "warn" for result in results)


def test_cloud_metadata_validator_warns_when_threshold_is_exceeded_or_plan_missing():
    manifest = _manifest(
        sources=[_record("optical", cloud_cover=60.0, qa={})],
        metadata_plan={"cloud_cover_max": 20.0, "cloud_shadow_handling": ""},
    )

    results = run_metadata_validators(manifest)

    assert any(result.name == "cloud_shadow_qa_metadata" and result.status == "warn" and "exceeds" in result.message for result in results)
    assert any(result.name == "cloud_shadow_qa_metadata" and result.status == "warn" and "handling plan" in result.message for result in results)


def test_split_strategy_validator_warns_for_random_non_spatial_split():
    results = run_metadata_validators(_manifest())

    assert any(
        result.name == "split_strategy"
        and result.status == "warn"
        and "spatial leakage" in result.message.lower()
        for result in results
    )
