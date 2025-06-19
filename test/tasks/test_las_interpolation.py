import os
import shutil
import test.utils.raster_utils as ru
from pathlib import Path

import pytest

from las_digital_models.tasks.las_interpolation import interpolate

TILE_COORD_SCALE = 10
TILE_WIDTH = 50
PIXEL_SIZE = 0.5

TEST_PATH = Path(__file__).resolve().parent.parent
TMP_PATH = TEST_PATH / "tmp" / "tasks" / "las_interpolation"
INPUT_FILE = TEST_PATH / "data" / "test_data_77055_627760_LA93_IGN69.laz"
GROUND_TRUTH_FOLDER = TEST_PATH / "data" / "interpolation"

COORD_X = 77055
COORD_Y = 627760
EXPECTED_XMIN = COORD_X * TILE_COORD_SCALE - PIXEL_SIZE / 2
EXPECTED_XMAX = COORD_Y * TILE_COORD_SCALE + PIXEL_SIZE / 2
EXPECTED_RASTER_BOUNDS = (EXPECTED_XMIN, EXPECTED_XMAX - TILE_WIDTH), (EXPECTED_XMIN + TILE_WIDTH, EXPECTED_XMAX)


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.makedirs(TMP_PATH)


@pytest.mark.parametrize(
    "filter_dimension, filter_values, output_file, ground_truth_file",
    [
        # default with no pre-filtering
        (
            "",
            [],
            TMP_PATH / "interpolate_default.tif",
            os.path.join(GROUND_TRUTH_FOLDER, "test_data_77055_627760_LA93_IGN69_50CM.tif"),
        ),
        # Filter by class (ground only)
        (
            "Classification",
            [2, 9, 66],
            TMP_PATH / "interpolate_classif.tif",
            os.path.join(GROUND_TRUTH_FOLDER, "test_data_77055_627760_LA93_IGN69_50CM_dtm_classes.tif"),
        ),
        # Filter by return number (check that other dimensions are ok)
        (
            "ReturnNumber",
            [2, 3, 4, 5],
            TMP_PATH / "interpolate_returnnumber.tif",
            os.path.join(GROUND_TRUTH_FOLDER, "test_data_77055_627760_LA93_IGN69_50CM_filter_returnnumber.tif"),
        ),
    ],
)
def test_interpolate(filter_dimension, filter_values, output_file, ground_truth_file):
    interpolate(
        INPUT_FILE,
        output_file,
        pixel_size=PIXEL_SIZE,
        tile_width=TILE_WIDTH,
        tile_coord_scale=TILE_COORD_SCALE,
        spatial_ref="EPSG:2154",
        no_data_value=-9999,
        filter_dimension=filter_dimension,
        filter_values=filter_values,
    )

    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    assert ru.allclose_mm(raster_bounds, EXPECTED_RASTER_BOUNDS)

    assert ru.tif_values_all_close(output_file, ground_truth_file)
