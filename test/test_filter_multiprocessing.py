import logging
import numpy as np
import os
import pytest
import shutil
from produit_derive_lidar.filter_multiprocessing import start_pool
from produit_derive_lidar.commons import commons


test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
input_dir = os.path.join(test_path, "data")

spatial_reference = "EPSG:2154"
output_dir = os.path.join(tmp_path, "ground")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_filter_multiprocessing():
    # Create the severals folder if not exists
    os.makedirs(output_dir, exist_ok=True)
    start_pool(input_dir, output_dir,
               spatial_ref=spatial_reference)
    # Check all files are generated
    for input_file in os.listdir(input_dir):
        if input_file.endswith(commons.point_cloud_extensions):
            output_file = os.path.join(output_dir, input_file)
            assert os.path.isfile(output_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_filter_multiprocessing()
