from pathlib import Path

import pytest

from geosciloop.core.schema import DataSourceRequest, load_task_config, parse_task_config


def test_loads_demo_config_with_expected_fields():
    config = load_task_config(Path("configs/uhi_synthetic_demo.yaml"), offline_override=True)

    assert config.project_name == "uhi_synthetic_demo"
    assert config.task_type == "urban_heat_island"
    assert config.offline is True
    assert config.target_variable == "lst_celsius"
    assert config.target == "lst_celsius"
    assert "ndvi" in config.explanatory_variables
    assert config.predictors == config.explanatory_variables
    assert config.risk_indicators == []
    assert config.grid_size_m > 0


def test_loads_morphology_demo_config_with_expected_fields():
    config = load_task_config(Path("configs/uhi_morphology_synthetic_demo.yaml"), offline_override=True)

    assert config.project_name == "uhi_morphology_synthetic_demo"
    assert config.task_type == "urban_heat_island"
    assert config.aoi_name == "Synthetic Morphology City"
    assert config.target_variable == "lst_celsius"
    assert config.target == "lst_celsius"
    assert config.offline is True
    assert config.random_seed == 123
    assert config.predictors == [
        "ndvi",
        "ndbi",
        "ndwi",
        "building_density",
        "building_height",
        "floor_area_ratio",
        "population_density",
        "road_density",
        "functional_zone",
    ]
    assert config.risk_indicators == ["population_exposure"]
    assert config.categorical_variables == ["functional_zone"]
    assert config.metadata_variables == ["cell_id", "x", "y"]
    assert "population_exposure" in config.explanatory_variables
    assert "population_exposure" not in config.predictors
    assert config.models == ["linear_regression", "random_forest"]


def test_config_rejects_missing_required_field():
    with pytest.raises(ValueError, match="research_question"):
        parse_task_config(
            {
                "project_name": "bad",
                "task_type": "urban_heat_island",
                "aoi_name": "Nowhere",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "target_variable": "lst_celsius",
                "explanatory_variables": ["ndvi"],
                "grid_size_m": 250,
                "models": ["linear_regression"],
                "output_dir": "outputs/bad",
                "random_seed": 1,
                "offline": True,
            }
        )


def test_loads_real_pilot_template_with_v0_2_schema_fields():
    config = load_task_config(Path("configs/uhi_real_pilot_template.yaml"), dry_run_override=True)

    assert config.project_name == "uhi_real_pilot_template"
    assert config.mode == "dry_run"
    assert config.offline is True
    assert config.dry_run is True
    assert config.execution["download"] is False
    assert config.execution["require_credentials"] is False
    assert config.aoi.name == "Fixture Pilot City"
    assert config.aoi.crs == "EPSG:4326"
    assert config.aoi.bbox == [-75.25, 39.85, -74.75, 40.25]
    assert config.time_range.start == "2024-07-01"
    assert config.time_range.end == "2024-08-31"
    assert config.target_variable == "lst_celsius"
    assert config.predictors == ["ndvi", "ndbi", "ndwi", "road_density", "population_density"]
    assert config.risk_indicators == ["population_exposure"]
    assert config.split_strategy.method == "random"
    assert config.split_strategy.spatial_awareness is False
    assert len(config.data_sources) == 4
    assert all(isinstance(source, DataSourceRequest) for source in config.data_sources)
    assert {source.role for source in config.data_sources} == {"lst", "optical", "roads", "population"}
    assert config.data_sources[0].adapter == "fixture_stac"
    assert "crs" in config.data_sources[0].required_metadata
