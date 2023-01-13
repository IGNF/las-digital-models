from lidar_prod import gf_one_tile
import logging
import os
import pytest
import shutil
import test.utils.point_cloud_utils as pcu


test_path = os.path.dirname(__file__)
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)
input_nb_points = 60653
expected_output_nb_points = 22343

spatial_reference = "EPSG:2154"
output_dir = tmp_path
output_file = os.path.join(output_dir, "test_data_0001_0001_LA93_IGN69_ground.las")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_gf_one_tile():
    gf_one_tile.run_gf_on_tile(input_file, output_dir, spatial_ref=spatial_reference)
    assert os.path.isfile(output_file)
    assert pcu.get_nb_points(output_file) == expected_output_nb_points


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_gf_one_tile()
