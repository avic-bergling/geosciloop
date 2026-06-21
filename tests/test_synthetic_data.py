import pandas as pd

from geosciloop.core.schema import load_task_config
from geosciloop.tools.synthetic_data import create_synthetic_uhi_data


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
