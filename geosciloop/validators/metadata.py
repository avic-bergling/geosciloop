from __future__ import annotations

from typing import Any

from geosciloop.core.schema import DataSourceManifest, DataSourceRecord
from geosciloop.core.state import ValidationResult


RASTER_ROLES = {"lst", "optical", "population"}
SATELLITE_ROLES = {"lst", "optical"}


def _raster_sources(manifest: DataSourceManifest) -> list[DataSourceRecord]:
    return [source for source in manifest.sources if source.role in RASTER_ROLES or source.resolution_m is not None]


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def check_crs_metadata(manifest: DataSourceManifest) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    sources = _raster_sources(manifest)
    missing = [source.role for source in sources if not _present(source.crs)]
    if missing:
        results.append(
            ValidationResult(
                "crs_metadata",
                "warn",
                "CRS metadata is missing for one or more raster-like sources.",
                {"missing_roles": missing},
            )
        )

    crs_values = sorted({str(source.crs) for source in sources if _present(source.crs)})
    target_crs = manifest.metadata_plan.get("target_crs")
    if len(crs_values) > 1 and not _present(target_crs):
        results.append(
            ValidationResult(
                "crs_metadata",
                "warn",
                "Multiple raster CRS values are present and no target CRS or reprojection plan is recorded.",
                {"crs_values": crs_values},
            )
        )

    if any(value == "EPSG:4326" for value in crs_values) and not str(target_crs).startswith("EPSG:326"):
        results.append(
            ValidationResult(
                "crs_metadata",
                "warn",
                "Geographic CRS is present; area or distance analysis needs a projected target CRS.",
                {"crs_values": crs_values, "target_crs": target_crs},
            )
        )

    if not results:
        results.append(
            ValidationResult(
                "crs_metadata",
                "pass",
                "CRS metadata is recorded for raster-like sources and a target CRS plan is available when needed.",
                {"crs_values": crs_values, "target_crs": target_crs},
            )
        )
    return results


def check_raster_resolution_metadata(manifest: DataSourceManifest) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    sources = _raster_sources(manifest)
    missing = [source.role for source in sources if source.resolution_m is None]
    if missing:
        results.append(
            ValidationResult(
                "raster_resolution_metadata",
                "warn",
                "Raster resolution metadata is missing for one or more raster-like sources.",
                {"missing_roles": missing},
            )
        )

    resolutions = sorted({float(source.resolution_m) for source in sources if source.resolution_m is not None})
    if len(resolutions) > 1 and not _present(manifest.metadata_plan.get("target_resolution_m")):
        results.append(
            ValidationResult(
                "raster_resolution_metadata",
                "warn",
                "Multiple raster resolutions are present and no target resolution or resampling plan is recorded.",
                {"resolution_m": resolutions},
            )
        )

    if not results:
        results.append(
            ValidationResult(
                "raster_resolution_metadata",
                "pass",
                "Raster resolution metadata is recorded and a target resolution plan is available when needed.",
                {"resolution_m": resolutions, "target_resolution_m": manifest.metadata_plan.get("target_resolution_m")},
            )
        )
    return results


def check_raster_alignment_metadata(manifest: DataSourceManifest) -> list[ValidationResult]:
    sources = _raster_sources(manifest)
    if len(sources) <= 1:
        return [ValidationResult("raster_alignment_metadata", "pass", "Only one raster-like source is planned.")]

    required = ["target_crs", "target_resolution_m", "alignment_strategy"]
    missing = [field for field in required if not _present(manifest.metadata_plan.get(field))]
    if missing:
        return [
            ValidationResult(
                "raster_alignment_metadata",
                "warn",
                "Multiple raster-like sources are planned but the target grid or alignment strategy is incomplete.",
                {"missing_plan_fields": missing},
            )
        ]
    return [
        ValidationResult(
            "raster_alignment_metadata",
            "pass",
            "Target CRS, target resolution, and alignment strategy are documented for multiple raster-like sources.",
            {"plan": {field: manifest.metadata_plan.get(field) for field in required}},
        )
    ]


def check_nodata_metadata(manifest: DataSourceManifest) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    sources = _raster_sources(manifest)
    missing = [source.role for source in sources if source.nodata is None]
    if missing:
        results.append(
            ValidationResult(
                "nodata_metadata",
                "warn",
                "NoData metadata is missing for one or more raster-like sources.",
                {"missing_roles": missing},
            )
        )
    if not _present(manifest.metadata_plan.get("nodata_handling")):
        results.append(
            ValidationResult(
                "nodata_metadata",
                "warn",
                "NoData handling plan is missing.",
                {},
            )
        )
    if not results:
        results.append(
            ValidationResult(
                "nodata_metadata",
                "pass",
                "NoData metadata and handling plan are recorded for raster-like sources.",
                {"roles": [source.role for source in sources]},
            )
        )
    return results


def check_cloud_shadow_qa_metadata(manifest: DataSourceManifest) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    threshold = manifest.metadata_plan.get("cloud_cover_max")
    satellite_sources = [source for source in manifest.sources if source.role in SATELLITE_ROLES]

    missing_cloud = [source.role for source in satellite_sources if source.cloud_cover is None]
    if missing_cloud:
        results.append(
            ValidationResult(
                "cloud_shadow_qa_metadata",
                "warn",
                "Cloud-cover metadata is missing for one or more satellite sources.",
                {"missing_roles": missing_cloud},
            )
        )

    exceeded = []
    if threshold is not None:
        exceeded = [
            {"role": source.role, "cloud_cover": source.cloud_cover, "threshold": threshold}
            for source in satellite_sources
            if source.cloud_cover is not None and float(source.cloud_cover) > float(threshold)
        ]
        if exceeded:
            results.append(
                ValidationResult(
                    "cloud_shadow_qa_metadata",
                    "warn",
                    "Cloud cover exceeds the configured threshold for one or more satellite sources.",
                    {"exceeded": exceeded},
                )
            )

    missing_qa = [source.role for source in satellite_sources if not _present(source.cloud_shadow_metadata)]
    if missing_qa:
        results.append(
            ValidationResult(
                "cloud_shadow_qa_metadata",
                "warn",
                "Cloud/shadow QA metadata is missing for one or more satellite sources.",
                {"missing_roles": missing_qa},
            )
        )

    if not _present(manifest.metadata_plan.get("cloud_shadow_handling")):
        results.append(
            ValidationResult(
                "cloud_shadow_qa_metadata",
                "warn",
                "Cloud/shadow handling plan is missing.",
                {},
            )
        )

    if not results:
        results.append(
            ValidationResult(
                "cloud_shadow_qa_metadata",
                "pass",
                "Cloud cover and cloud/shadow QA metadata are recorded for satellite sources.",
                {"threshold": threshold, "roles": [source.role for source in satellite_sources]},
            )
        )
    return results


def check_source_provenance(manifest: DataSourceManifest) -> list[ValidationResult]:
    required = ["provider", "datetime", "license", "href", "query", "provenance"]
    missing_by_role: dict[str, list[str]] = {}
    for source in manifest.sources:
        missing = [field for field in required if not _present(getattr(source, field))]
        if not (_present(source.collection) or _present(source.dataset)):
            missing.append("collection_or_dataset")
        if missing:
            missing_by_role[source.role] = missing

    if missing_by_role:
        return [
            ValidationResult(
                "source_provenance",
                "warn",
                "Source provenance metadata is incomplete for one or more planned sources.",
                {"missing_by_role": missing_by_role},
            )
        ]
    return [
        ValidationResult(
            "source_provenance",
            "pass",
            "Provider, dataset or collection, datetime, license, query, href, and provenance are recorded.",
            {"roles": [source.role for source in manifest.sources]},
        )
    ]


def check_split_strategy(manifest: DataSourceManifest) -> list[ValidationResult]:
    split = manifest.split_strategy
    if split and split.method == "random" and split.spatial_awareness is False:
        return [
            ValidationResult(
                "split_strategy",
                "warn",
                "Random split is planned for a geospatial AOI; spatial leakage may inflate future model performance.",
                {"method": split.method, "spatial_awareness": split.spatial_awareness, "notes": split.notes},
            )
        ]
    return [
        ValidationResult(
            "split_strategy",
            "pass",
            "Split strategy records spatial awareness or a non-random spatial/block method.",
            {"method": split.method if split else None, "spatial_awareness": split.spatial_awareness if split else None},
        )
    ]


def run_metadata_validators(manifest: DataSourceManifest) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    results.extend(check_crs_metadata(manifest))
    results.extend(check_raster_resolution_metadata(manifest))
    results.extend(check_raster_alignment_metadata(manifest))
    results.extend(check_nodata_metadata(manifest))
    results.extend(check_cloud_shadow_qa_metadata(manifest))
    results.extend(check_source_provenance(manifest))
    results.extend(check_split_strategy(manifest))
    return results
