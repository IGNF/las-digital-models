import os
import test.utils.raster_utils as ru

import laspy
import numpy as np
import pytest
from hydra import compose, initialize

from las_digital_models.main import main_las_digital_models


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    return base_tmp_path / "main"


def get_2d_bounding_box(path):
    """Get bbox for a las file (x, y only)"""
    with laspy.open(path) as f:
        mins = f.header.mins
        maxs = f.header.maxs

    return mins[:2], maxs[:2]


def test_main_intermediate_files(tmp_path, base_data_path, test_tile):
    in_mins, in_maxs = get_2d_bounding_box(test_tile.input_path)
    buffer_size = 10
    output_dir = tmp_path / "main_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
    output_dtm_dir = output_dir / "DTM"
    output_dsm_dir = output_dir / "DSM"
    output_dhm_dir = output_dir / "DHM"

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="test",
            overrides=[
                f"io.input_filename={test_tile.input_filename}",
                f"io.input_dir={base_data_path}",
                f"io.output_dir={output_dir}",
                f"tile_geometry.tile_coord_scale={test_tile.tile_coord_scale}",
                f"tile_geometry.tile_width={test_tile.tile_width}",
                f"buffer.size={buffer_size}",
                "buffer.output_subdir='buffer'",
            ],
        )
        main_las_digital_models(cfg)

    # Check buffer files are correct
    output_buffer_path = output_buffer_dir / test_tile.input_filename
    assert os.path.isfile(output_buffer_path)
    out_mins, out_maxs = get_2d_bounding_box(output_buffer_path)
    assert np.all(out_mins == in_mins - buffer_size)
    assert np.all(out_maxs[0] == in_maxs[0] + buffer_size)
    assert out_maxs[1] == in_maxs[1]  # neighbor file does not exist

    # Check output tif files are correct
    output_dtm_path = output_dtm_dir / test_tile.output_filename
    assert os.path.isfile(output_dtm_path)
    dtm_bounds = ru.get_tif_extent(output_dtm_path)

    assert dtm_bounds == test_tile.expected_raster_bounds

    output_dsm_path = output_dsm_dir / test_tile.output_filename
    assert os.path.isfile(output_dsm_path)
    dsm_bounds = ru.get_tif_extent(output_dsm_path)

    assert dsm_bounds == test_tile.expected_raster_bounds

    output_dhm_path = output_dhm_dir / test_tile.output_filename
    assert os.path.isfile(output_dhm_path)
    dhm_bounds = ru.get_tif_extent(output_dhm_path)

    assert dhm_bounds == test_tile.expected_raster_bounds


def test_main_without_intermediate_files(tmp_path, base_data_path, test_tile):
    """Compute only dhm, and check buffer / dsm / dtm files are only temporary files"""
    buffer_size = 10
    output_dir = tmp_path / "main_without_intermediate_files"
    output_buffer_dir = output_dir / "buffer"
    output_dtm_dir = output_dir / "DTM"
    output_dsm_dir = output_dir / "DSM"
    output_dhm_dir = output_dir / "DHM"
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="test",
            overrides=[
                f"io.input_filename={test_tile.input_filename}",
                f"io.input_dir={base_data_path}",
                f"io.output_dir={output_dir}",
                f"tile_geometry.tile_coord_scale={test_tile.tile_coord_scale}",
                f"tile_geometry.tile_width={test_tile.tile_width}",
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
    assert os.path.exists(output_dhm_dir / test_tile.output_filename)
