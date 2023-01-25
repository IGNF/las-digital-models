from produit_derive_lidar import filter_one_tile
import logging
import os
import pytest
import shutil
import utils.point_cloud_utils as pcu


test_path = os.path.dirname(__file__)
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)
input_nb_points = 60653
expected_output_nb_points_ground = 22343
expected_output_nb_points_building = 14908

spatial_reference = "EPSG:2154"
output_dir = os.path.join(tmp_path,  "ground")
output_file = os.path.join(output_dir, "test_data_0001_0001_LA93_IGN69.las")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_filter_one_tile():
    filter_one_tile.run_filter_on_tile(input_file, output_dir, spatial_ref=spatial_reference)
    assert os.path.isfile(output_file)
    assert pcu.get_nb_points(output_file) == expected_output_nb_points_ground


def test_filter_one_tile_building_class():
    filter_one_tile.run_filter_on_tile(input_file, output_dir, spatial_ref=spatial_reference,
    keep_classes=[6])
    assert os.path.isfile(output_file)
    assert pcu.get_nb_points(output_file) == expected_output_nb_points_building


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_filter_one_tile()
    test_filter_one_tile_building_class()
