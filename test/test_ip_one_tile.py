from osgeo import gdal
from lidar_prod import ip_one_tile
from lidar_prod.commons import commons
import logging
import numpy as np
import os
import pytest
import shutil
import utils.point_cloud_utils as pcu
import utils.raster_utils as ru


test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)
input_nb_points = 60653

spatial_reference = "EPSG:2154"
output_dir = tmp_path
ground_dir = os.path.join(test_path, "data", "ground")
pixel_size = 1

postprocessing = 0


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)



def compute_test_ip_one_tile(interpolation_method):
    postfix = f"_1M_{commons.method_postfix[interpolation_method]}.tif"
    output_filename = os.path.splitext(os.path.basename(input_file))[0] + postfix
    output_file = os.path.join(output_dir, output_filename)
    logging.debug(output_file)

    ip_one_tile.run_ip_on_tile(input_file, ground_dir, tmp_path, output_dir,
        pixel_size, interpolation_method, postprocessing,
        spatial_ref=spatial_reference)
    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    pcd_bounds = pcu.get_2d_bounding_box(input_file)
    assert np.allclose(raster_bounds, pcd_bounds, rtol=1e-06)


def test_ip_one_tile_startin_TINlinear():
    interpolation_method = "startin-TINlinear"
    compute_test_ip_one_tile(interpolation_method)


def test_ip_one_tile_startin_laplace():
    interpolation_method = "startin-Laplace"
    compute_test_ip_one_tile(interpolation_method)


def test_ip_one_tile_startin_CGALNN():
    interpolation_method = "CGAL-NN"
    compute_test_ip_one_tile(interpolation_method)


def test_ip_one_tile_startin_pdal_idw():
    interpolation_method = "PDAL-IDW"
    compute_test_ip_one_tile(interpolation_method)


# Disabled. Method not currently maintained
# def test_ip_one_tile_startin_IDWquad():
#     interpolation_method = "IDWquad"
#     compute_test_ip_one_tile(interpolation_method)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile_startin_TINlinear()
    test_ip_one_tile_startin_laplace()
    test_ip_one_tile_startin_CGALNN()
    test_ip_one_tile_startin_pdal_idw()
    # test_ip_one_tile_startin_IDWquad()
