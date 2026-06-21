import pandas as pd

from geosciloop.core.schema import load_task_config
from geosciloop.tools.synthetic_data import create_synthetic_uhi_data


ALLOWED_FUNCTIONAL_ZONES = {"residential", "commercial", "industrial", "mixed_use", "park", "water"}


def test_synthetic_data_is_reproducible_with_fixed_seed():
    config = load_task_config("configs/uhi_synthetic_demo.yaml", offline_override=True)

    first = create_synthetic_uhi_data(config)
    second = create_synthetic_uhi_data(config)

    pd.testing.assert_frame_equal(first, second)


def test_synthetic_data_has_expected_columns_and_relationships():
    config = load_task_config("configs/uhi_synthetic_demo.yaml", offline_override=True)
    data = create_synthetic_uhi_data(config)

    expected = {"cell_id", "x", "y", "lst_celsius", *config.explanatory_variables}
    assert expected.issubset(data.columns)
    assert data["ndvi"].between(-1, 1).all()
    assert data["ndbi"].between(-1, 1).all()
    assert data["lst_celsius"].between(-30, 80).all()
    assert data["ndvi"].corr(data["lst_celsius"]) < 0
    assert data["ndbi"].corr(data["lst_celsius"]) > 0


def test_morphology_synthetic_data_is_reproducible_with_fixed_seed():
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)

    first = create_synthetic_uhi_data(config)
    second = create_synthetic_uhi_data(config)

    pd.testing.assert_frame_equal(first, second)


def test_morphology_synthetic_data_has_expected_variables_and_relationships():
    config = load_task_config("configs/uhi_morphology_synthetic_demo.yaml", offline_override=True)
    data = create_synthetic_uhi_data(config)

    expected = {"cell_id", "x", "y", "lst_celsius", *config.explanatory_variables}
    assert expected.issubset(data.columns)
    assert set(data["functional_zone"]).issubset(ALLOWED_FUNCTIONAL_ZONES)
    assert data["building_height"].ge(0).all()
    assert data["floor_area_ratio"].ge(0).all()
    assert data["population_exposure"].ge(0).all()
    assert data["ndvi"].between(-1, 1).all()
    assert data["ndbi"].between(-1, 1).all()
    assert data["ndwi"].between(-1, 1).all()
    assert data["lst_celsius"].between(-30, 80).all()
    assert data["ndvi"].corr(data["lst_celsius"]) < 0
    assert data["ndwi"].corr(data["lst_celsius"]) < 0
    assert data["ndbi"].corr(data["lst_celsius"]) > 0
    assert data["building_density"].corr(data["lst_celsius"]) > 0
    assert data["floor_area_ratio"].corr(data["lst_celsius"]) > 0
