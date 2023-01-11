import os
import pytest
import shutil
from lidar_prod.tasks import las_ground
import test.utils.point_cloud_utils as pcu


test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "test_data_0001_0001_LA93_IGN69.laz"
)
input_nb_points = 60653
expected_output_nb_points = 22343


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_las_ground_create_file():
    """Check that a ground file is created after running filter_las_ground"""
    output_file = os.path.join(tmp_path, "ground.las")
    las_ground.filter_las_ground(input_file, output_file)
    assert os.path.isfile(output_file)


def test_las_ground_nb_points():
    """Check that a ground file is created after running filter_las_ground"""
    output_file = os.path.join(tmp_path, "ground.las")
    las_ground.filter_las_ground(input_file, output_file)
    assert pcu.get_nb_points(output_file) == expected_output_nb_points


if __name__ == "__main__":
    setup_module(None)
    test_las_ground_create_file()
    test_las_ground_nb_points()