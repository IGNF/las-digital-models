from lidar_prod.commons import commons
import logging
import numpy as np
import os
import pytest
import shutil
from lidar_prod.ip_multiprocessing import start_pool
from lidar_prod.commons import commons


test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
input_dir = os.path.join(test_path, "data")

spatial_reference = "EPSG:2154"
output_dir = tmp_path
ground_dir = os.path.join(test_path, "data", "ground")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_ip_multiprocessing():
    filetype = "laz"
        # Create the severals folder if not exists
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(tmp_path, exist_ok=True)
    start_pool(input_dir, ground_dir, output_dir, tmp_path, filetype=filetype,
               spatial_ref=spatial_reference)
    # Check all files are generated
    for input_file in os.listdir(input_dir):
        if input_file.endswith(filetype):
            postfix = f"_1M_{commons.method_postfix['startin-Laplace']}.tif"
            output_filename = os.path.splitext(os.path.basename(input_file))[0] + postfix
            output_file = os.path.join(output_dir, output_filename)
            assert os.path.isfile(output_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_multiprocessing()
