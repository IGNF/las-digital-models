import os
import test.utils.raster_utils as ru

import pytest

from las_digital_models.tasks.las_interpolation import interpolate


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    p = base_tmp_path / "tasks" / "las_interpolation"
    p.mkdir(parents=True)
    return p


@pytest.mark.parametrize(
    "filter_dimension, filter_values, output_filename, ground_truth_file_suffix",
    [
        # default with no pre-filtering
        (
            "",
            [],
            "interpolate_default.tif",
            "",
        ),
        # Filter by class (ground only)
        (
            "Classification",
            [2, 9, 66],
            "interpolate_classif.tif",
            "_dtm_classes",
        ),
        # Filter by return number (check that other dimensions are ok)
        (
            "ReturnNumber",
            [2, 3, 4, 5],
            "interpolate_returnnumber.tif",
            "_filter_returnnumber",
        ),
    ],
)
def test_interpolate(tmp_path, filter_dimension, filter_values, output_filename, ground_truth_file_suffix, test_tile):
    output_file = tmp_path / output_filename
    interpolate(
        test_tile.input_path,
        output_file,
        tile_origin=test_tile.origin,
        pixel_size=0.5,
        tile_width=50,
        spatial_ref="EPSG:2154",
        no_data_value=-9999,
        filter_dimension=filter_dimension,
        filter_values=filter_values,
    )

    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    assert ru.allclose_mm(raster_bounds, test_tile.expected_raster_bounds)

    assert ru.tif_values_all_close(output_file, test_tile.expected_interpolation(ground_truth_file_suffix))
