from pathlib import Path

import pytest

from geosciloop.core.schema import load_task_config, parse_task_config


def test_loads_demo_config_with_expected_fields():
    config = load_task_config(Path("configs/uhi_synthetic_demo.yaml"), offline_override=True)

    assert config.project_name == "uhi_synthetic_demo"
    assert config.task_type == "urban_heat_island"
    assert config.offline is True
    assert config.target_variable == "lst_celsius"
    assert "ndvi" in config.explanatory_variables
    assert config.grid_size_m > 0


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
