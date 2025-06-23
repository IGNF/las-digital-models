import logging
import os
import shutil
import test.utils.raster_utils as ru

from hydra import compose, initialize

from las_digital_models import dhm_one_tile

coordX = 77055
coordY = 627760
tile_coord_scale = 10
tile_width = 50
pixel_size = 0.5

test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")

output_dir = os.path.join(tmp_path, "DHM")
expected_output_file = os.path.join(output_dir, f"test_data_{coordX}_{coordY}_LA93_IGN69_50CM.tif")

expected_xmin = coordX * tile_coord_scale - pixel_size / 2
expected_ymax = coordY * tile_coord_scale + pixel_size / 2
expected_raster_bounds = (expected_xmin, expected_ymax - tile_width), (expected_xmin + tile_width, expected_ymax)


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except FileNotFoundError:
        pass
    os.mkdir(tmp_path)


def test_mnh_one_tile():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                f"io.output_dir={output_dir}",
                "dhm=test",
            ],
        )

    dhm_one_tile.run_dhm_on_tile(cfg)
    assert os.path.isfile(expected_output_file)

    raster_bounds = ru.get_tif_extent(expected_output_file)
    assert ru.allclose_mm(raster_bounds, expected_raster_bounds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_mnh_one_tile()
