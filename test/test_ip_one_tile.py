from osgeo import gdal
from produit_derive_lidar import ip_one_tile
from produit_derive_lidar.commons import commons
import logging
import numpy as np
import os
import pytest
import shutil
import test.utils.point_cloud_utils as pcu
import test.utils.raster_utils as ru


coordX = 77060
coordY = 627760
test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
origin_file = os.path.join(
    test_path,
    "data",
    f"test_data_{coordX}_{coordY}_LA93_IGN69.laz"
)

# input_las_dir = os.path.join(test_path, "data", "ground")
# input_ext = "las"


input_las_dir = os.path.join(test_path, "data")
input_ext = "laz"

spatial_reference = "EPSG:2154"
output_dir = tmp_path
pixel_size = 0.5

expected_xmin = coordX * commons.tile_coord_scale - pixel_size/2
expected_ymax = coordY * commons.tile_coord_scale  + pixel_size/2
expected_raster_bounds = (expected_xmin, expected_ymax - commons.tile_width), (expected_xmin + commons.tile_width, expected_ymax)


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def compute_test_ip_one_tile(interpolation_method):
    logging.warn("At the moment tile_coord_scale and tile_width must be temporarily changed for the test to pass")
    postfix = f"_50CM_{commons.method_postfix[interpolation_method]}.tif"
    output_filename = os.path.splitext(os.path.basename(origin_file))[0] + postfix
    output_file = os.path.join(output_dir, output_filename)
    logging.debug(output_file)

    ip_one_tile.run_ip_on_tile(origin_file, input_las_dir, output_dir,
        pixel_size, interpolation_method,
        spatial_ref=spatial_reference, input_ext=input_ext)
    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    assert np.allclose(raster_bounds, expected_raster_bounds, rtol=1e-06)


def test_ip_one_tile_all_methods():
    for method in commons.method_postfix.keys():
        logging.debug(f"Test for method: {method}")
        compute_test_ip_one_tile(method)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile_all_methods()

