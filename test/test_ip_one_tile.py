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


test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
origin_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)

input_las_dir = os.path.join(test_path, "data", "ground")
input_ext = "las"

spatial_reference = "EPSG:2154"
output_dir = tmp_path
pixel_size = 1


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)



def compute_test_ip_one_tile(interpolation_method):
    postfix = f"_1M_{commons.method_postfix[interpolation_method]}.tif"
    output_filename = os.path.splitext(os.path.basename(origin_file))[0] + postfix
    output_file = os.path.join(output_dir, output_filename)
    logging.debug(output_file)

    ip_one_tile.run_ip_on_tile(origin_file, input_las_dir, tmp_path, output_dir,
        pixel_size, interpolation_method,
        spatial_ref=spatial_reference, input_ext="las")
    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    pcd_bounds = pcu.get_2d_bounding_box(origin_file)
    assert np.allclose(raster_bounds, pcd_bounds, rtol=1e-06)


def test_ip_one_tile_all_methods():
    for method in commons.method_postfix.keys():
        compute_test_ip_one_tile(method)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile_all_methods()

