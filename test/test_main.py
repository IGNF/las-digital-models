import os
import shutil
import test.utils.raster_utils as ru
from pathlib import Path

import laspy
import numpy as np
from hydra import compose, initialize

from las_digital_models.main import main_las_digital_models

COORD_X = 77055
COORD_Y = 627760
TILE_COORD_SCALE = 10
TILE_WIDTH = 50
PIXEL_SIZE = 0.5
TEST_PATH = Path(__file__).resolve().parent
TMP_PATH = TEST_PATH / "tmp" / "main"
DATA_PATH = TEST_PATH / "data"

INPUT_FILENAME = f"test_data_{COORD_X}_{COORD_Y}_LA93_IGN69.laz"
INPUT_TILENAME = os.path.splitext(INPUT_FILENAME)[0]
OUTPUT_TIF_NAME = f"{INPUT_TILENAME}_50CM.tif"

expected_xmin = COORD_X * TILE_COORD_SCALE - PIXEL_SIZE / 2
expected_ymax = COORD_Y * TILE_COORD_SCALE + PIXEL_SIZE / 2
EXPECTED_RASTER_BOUNDS = (expected_xmin, expected_ymax - TILE_WIDTH), (expected_xmin + TILE_WIDTH, expected_ymax)


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.makedirs(TMP_PATH)


def get_2d_bounding_box(path):
    """Get bbox for a las file (x, y only)"""
    with laspy.open(path) as f:
        mins = f.header.mins
        maxs = f.header.maxs

    return mins[:2], maxs[:2]


def test_main_intermediate_files():
    in_mins, in_maxs = get_2d_bounding_box(DATA_PATH / INPUT_FILENAME)
    buffer_size = 10
    output_dir = TMP_PATH / "main_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
    output_dtm_dir = output_dir / "DTM"
    output_dsm_dir = output_dir / "DSM"
    output_dhm_dir = output_dir / "DHM"

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="test",
            overrides=[
                f"io.input_filename={INPUT_FILENAME}",
                f"io.input_dir={DATA_PATH}",
                f"io.output_dir={output_dir}",
                f"tile_geometry.tile_coord_scale={TILE_COORD_SCALE}",
                f"tile_geometry.tile_width={TILE_WIDTH}",
                f"buffer.size={buffer_size}",
                "buffer.output_subdir='buffer'",
            ],
        )
        main_las_digital_models(cfg)

    # Check buffer files are correct
    output_buffer_path = output_buffer_dir / INPUT_FILENAME
    assert os.path.isfile(output_buffer_path)
    out_mins, out_maxs = get_2d_bounding_box(output_buffer_path)
    assert np.all(out_mins == in_mins - buffer_size)
    assert np.all(out_maxs[0] == in_maxs[0] + buffer_size)
    assert out_maxs[1] == in_maxs[1]  # neighbor file does not exist

    # Check output tif files are correct
    output_dtm_path = output_dtm_dir / OUTPUT_TIF_NAME
    assert os.path.isfile(output_dtm_path)
    dtm_bounds = ru.get_tif_extent(output_dtm_path)

    assert dtm_bounds == EXPECTED_RASTER_BOUNDS

    output_dsm_path = output_dsm_dir / OUTPUT_TIF_NAME
    assert os.path.isfile(output_dsm_path)
    dsm_bounds = ru.get_tif_extent(output_dsm_path)

    assert dsm_bounds == EXPECTED_RASTER_BOUNDS

    output_dhm_path = output_dhm_dir / OUTPUT_TIF_NAME
    assert os.path.isfile(output_dhm_path)
    dhm_bounds = ru.get_tif_extent(output_dhm_path)

    assert dhm_bounds == EXPECTED_RASTER_BOUNDS


def test_main_without_intermediate_files():
    """Compute only dhm, and check buffer / dsm / dtm files are only temporary files"""
    buffer_size = 10
    output_dir = TMP_PATH / "main_without_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
    output_dtm_dir = output_dir / "DTM"
    output_dsm_dir = output_dir / "DSM"
    output_dhm_dir = output_dir / "DHM"
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="test",
            overrides=[
                f"io.input_filename={INPUT_FILENAME}",
                f"io.input_dir={DATA_PATH}",
                f"io.output_dir={output_dir}",
                f"tile_geometry.tile_coord_scale={TILE_COORD_SCALE}",
                f"tile_geometry.tile_width={TILE_WIDTH}",
                f"buffer.size={buffer_size}",
                "tasks.dtm=false",
                "tasks.dsm=false",
                "tasks.dhm=true",
            ],
        )
        main_las_digital_models(cfg)

    # Check outputs are correct
    assert not os.path.exists(output_buffer_dir)
    assert not os.path.exists(output_dtm_dir)
    assert not os.path.exists(output_dsm_dir)
    assert os.path.exists(output_dhm_dir / OUTPUT_TIF_NAME)
