import os
import shutil
from pathlib import Path

import laspy
import numpy as np
from hydra import compose, initialize

from las_digital_models.main import main_las_digital_models

COORD_X = 77055
COORD_Y = 627760
TILE_COORD_SCALE = 10
TILE_WIDTH = 50

TEST_PATH = Path(__file__).resolve().parent
TMP_PATH = TEST_PATH / "tmp" / "main"
DATA_PATH = TEST_PATH / "data"

INPUT_FILENAME = f"test_data_{COORD_X}_{COORD_Y}_LA93_IGN69.laz"


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
    buffer_size = 10
    output_dir = TMP_PATH / "main_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
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
                f"buffer.output_subdir={output_buffer_dir}",
            ],
        )
        main_las_digital_models(cfg)

    # Check buffer files are correct
    output_path = output_buffer_dir / INPUT_FILENAME
    assert os.path.isfile(output_path)
    in_mins, in_maxs = get_2d_bounding_box(DATA_PATH / INPUT_FILENAME)
    out_mins, out_maxs = get_2d_bounding_box(output_path)
    assert np.all(out_mins == in_mins - buffer_size)
    assert np.all(out_maxs[0] == in_maxs[0] + buffer_size)
    assert out_maxs[1] == in_maxs[1]  # neighbor file does not exist


def test_main_without_intermediate_files():
    buffer_size = 10
    output_dir = TMP_PATH / "main_without_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
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
            ],
        )
        main_las_digital_models(cfg)

    # Check buffer files are correct
    assert not os.path.exists(output_buffer_dir)
