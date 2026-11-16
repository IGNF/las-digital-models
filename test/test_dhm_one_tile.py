import os
import test.utils.raster_utils as ru

import pytest
from hydra import compose, initialize

from las_digital_models import dhm_one_tile


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    return base_tmp_path / "dhm_one_tile"


def test_dhm_one_tile(tmp_path, test_tile):
    output_dir = tmp_path / "test_dhm_one_tile"
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                "dhm=test",
                f"io.output_dir={output_dir}",
            ],
        )

    dhm_one_tile.main(cfg)
    output_file = output_dir / test_tile.output_filename
    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    assert ru.allclose_mm(raster_bounds, test_tile.expected_raster_bounds)
