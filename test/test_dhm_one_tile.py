from produit_derive_lidar import dhm_one_tile
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
    "test_data_77055_627760_LA93_IGN69.laz"
)
dtm_dir = os.path.join(test_path, "data", "DTM")
dsm_dir = os.path.join(test_path, "data", "DSM")

output_dir = os.path.join(tmp_path, "DHM")

pixel_size = 0.5
interpolation_method = "PDAL-TIN"

def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_mnh_one_tile():
    os.makedirs(output_dir, exist_ok=True)
    _size = commons.give_name_resolution_raster(pixel_size)
    postfix = f"{_size}_{commons.method_postfix[interpolation_method]}.tif"
    output_filename = os.path.splitext(os.path.basename(origin_file))[0] + postfix
    output_file = os.path.join(output_dir, output_filename)

    dhm_one_tile.run_dhm_on_tile(origin_file, dsm_dir, dtm_dir, output_dir,
        pixel_size, interpolation_method)
    assert os.path.isfile(output_file)

    raster_bounds = ru.get_tif_extent(output_file)
    pcd_bounds = pcu.get_2d_bounding_box(origin_file)
    assert np.allclose(raster_bounds, pcd_bounds, rtol=1e-06)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_mnh_one_tile()
