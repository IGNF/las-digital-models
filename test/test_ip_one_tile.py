import logging
import os
import test.utils.raster_utils as ru

import pytest
from hydra import compose, initialize

from las_digital_models import ip_one_tile


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    return base_tmp_path / "ip_one_tile"


def test_main(tmp_path, test_tile):
    output_dir = tmp_path / "test_main"
    os.makedirs(output_dir, exist_ok=True)
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                f"io.output_dir={output_dir}",
                "tile_geometry=test",
                "interpolation.custom.filter.dimension=''",
                "interpolation.custom.filter.keep_values=[]",
            ],
        )
        output_file = output_dir / test_tile.output_filename
        logging.debug(output_file)
        logging.debug(f"Pixel size: {cfg.tile_geometry.pixel_size}")

        ip_one_tile.main(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, test_tile.expected_raster_bounds)

        assert ru.tif_values_all_close(output_file, test_tile.expected_interpolation())


def test_main_with_no_data_mask(tmp_path, test_tile):
    output_dir = tmp_path / "test_main_with_no_data_mask"

    os.makedirs(output_dir, exist_ok=True)
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                f"io.no_data_mask_shapefile={test_tile.shapefile}",
                f"io.output_dir={output_dir}",
                "interpolation.custom.filter.keep_values=[]",
            ],
        )

        output_file = output_dir / test_tile.output_filename
        logging.debug(f"Write to {output_file}")

        ip_one_tile.main(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, test_tile.expected_raster_bounds)

        assert ru.tif_values_all_close(output_file, test_tile.expected_interpolation("_no_data"))
