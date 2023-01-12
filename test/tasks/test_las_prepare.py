import numpy as np
import os
import pytest
import shutil
from lidar_prod.tasks import las_prepare
import test.utils.point_cloud_utils as pcu


test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_path = os.path.join(test_path, "tmp")
input_dir =  os.path.join(test_path, "data", "ground")
input_file = os.path.join(input_dir, "test_data_0001_0001_LA93_IGN69_ground.las")
output_file = os.path.join(tmp_path, "cropped.las")

input_nb_points = 22343
expected_output_nb_points = 47037
expected_out_mins = [770540., 6277540.]
expected_out_maxs = [770610., 6277600.]



def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_create_las_with_buffer():
    buffer_width = 10
    las_prepare.create_las_with_buffer(
        input_dir, input_file, os.path.join(tmp_path, "merged.las"), output_file, buffer_width=buffer_width)
    # check file exists
    assert os.path.isfile(output_file)

    # check difference in bbox
    in_mins, in_maxs = pcu.get_2d_bounding_box(input_file)
    out_mins, out_maxs = pcu.get_2d_bounding_box(output_file)

    # The following test does not work on the current test case as there is no tile on the left
    # and the top of the tile
    assert np.all(np.isclose(out_mins,  in_mins - buffer_width))
    assert np.all(np.isclose(out_maxs, in_maxs + buffer_width))

    # check number of points
    assert pcu.get_nb_points(output_file) == expected_output_nb_points

    # Check contre valeur attendue
    assert np.all(out_mins == expected_out_mins)
    assert np.all(out_maxs == expected_out_maxs)


if __name__ == "__main__":
    test_create_las_with_buffer()