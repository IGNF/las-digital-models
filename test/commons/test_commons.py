import os
import pytest
from lidar_prod.commons import commons
import test.utils.point_cloud_utils as pcu
import logging


test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)


def test_get_infos():
    out_pdal = commons.las_info(input_file, spatial_ref="EPSG:2154")
    out_laspy = pcu.get_2d_bounding_box(input_file)
    out_change_srs = commons.las_info(input_file, spatial_ref="EPSG:4326")
    logging.info(out_pdal)
    logging.info(out_laspy)
    logging.info(out_change_srs)



if __name__ == "__main__":
    # test_path = '/home/LVauchier/Documents/02_data/MNT_produits_derives_lidar/data'
    # for f in os.listdir(test_path):
    #     print(pcu.get_2d_bounding_box(os.path.join(test_path, f)))
    test_get_infos()