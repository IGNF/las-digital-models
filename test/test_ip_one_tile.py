import logging
import os
import shutil
import test.utils.raster_utils as ru
from pathlib import Path

from hydra import compose, initialize

from las_digital_models import ip_one_tile

COORD_X = 77055
COORD_Y = 627760
TILE_COORD_SCALE = 10
TILE_WIDTH = 50
PIXEL_SIZE = 0.5

TEST_PATH = Path(__file__).resolve().parent
TMP_PATH = TEST_PATH / "tmp"
GROUND_TRUTH_FOLDER = TEST_PATH / "data" / "interpolation"

EXPECTED_XMIN = COORD_X * TILE_COORD_SCALE - PIXEL_SIZE / 2
EXPECTED_XMAX = COORD_Y * TILE_COORD_SCALE + PIXEL_SIZE / 2
EXPECTED_RASTER_BOUNDS = (EXPECTED_XMIN, EXPECTED_XMAX - TILE_WIDTH), (EXPECTED_XMIN + TILE_WIDTH, EXPECTED_XMAX)

SHAPEFILE = TEST_PATH / "data" / "mask_shapefile" / "test_multipolygon_shapefile.shp"
EXPECTED_OUTPUT_USING_SHAPEFILE = GROUND_TRUTH_FOLDER / "test_data_77055_627760_LA93_IGN69_50CM_no_data.tif"


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.mkdir(TMP_PATH)


def get_expected_output_file(base_dir=None):
    if base_dir is None:
        base_dir = TMP_PATH / "hydra_ip"
    expected_output_file = os.path.join(base_dir, f"test_data_{COORD_X}_{COORD_Y}_LA93_IGN69_50CM.tif")

    return expected_output_file


def test_ip_one_tile():
    output_dir = os.path.join(TMP_PATH, "test_ip_one_tile")
    os.makedirs(output_dir, exist_ok=True)
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                f"io.output_dir={output_dir}",
                "tile_geometry=test",
                "filter.dimension=''",
                "filter.keep_values=[]",
            ],
        )
        output_file = get_expected_output_file(base_dir=output_dir)
        logging.debug(output_file)
        logging.debug(f"Pixel size: {cfg.tile_geometry.pixel_size}")

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, EXPECTED_RASTER_BOUNDS)

        assert ru.tif_values_all_close(output_file, os.path.join(GROUND_TRUTH_FOLDER, os.path.basename(output_file)))


def test_ip_with_no_data_mask():
    output_dir = os.path.join(TMP_PATH, "test_ip_with_no_data_mask")
    os.makedirs(output_dir, exist_ok=True)
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                f"io.no_data_mask_shapefile={SHAPEFILE}",
                f"io.output_dir={output_dir}",
                "filter.keep_values=[]",
            ],
        )

        output_file = get_expected_output_file(base_dir=output_dir)
        logging.debug(f"Write to {output_file}")

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, EXPECTED_RASTER_BOUNDS)

        assert ru.tif_values_all_close(output_file, EXPECTED_OUTPUT_USING_SHAPEFILE)


def test_ip_dtm_classes():
    output_dir = os.path.join(TMP_PATH, "test_ip_dtm_classes")
    os.makedirs(output_dir, exist_ok=True)
    expected_output = os.path.join(
        TEST_PATH, "data", "interpolation", "test_data_77055_627760_LA93_IGN69_50CM_dtm_classes.tif"
    )
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                "filter=dtm",
                f"io.output_dir={output_dir}",
            ],
        )

        output_file = get_expected_output_file(base_dir=output_dir)

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, EXPECTED_RASTER_BOUNDS)

        assert ru.tif_values_all_close(output_file, expected_output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile()
    test_ip_with_no_data_mask()
