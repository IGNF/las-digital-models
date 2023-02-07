import logging
import numpy as np
import os
import pytest
import shutil
from produit_derive_lidar.dhm_multiprocessing import start_pool
from produit_derive_lidar.commons import commons


test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
origin_dir = os.path.join(test_path, "data")
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


def test_dhm_multiprocessing():
    filetype = "laz"
    # Create the severals folder if not exists
    os.makedirs(output_dir, exist_ok=True)
    start_pool(origin_dir, dsm_dir, dtm_dir, output_dir, pixel_size,
             filetype=filetype, interpolation_method=interpolation_method)
    # Check all files are generated
    for input_file in os.listdir(origin_dir):
        if input_file.endswith(filetype):
            _size = commons.give_name_resolution_raster(pixel_size)
            postfix = f"{_size}_{commons.method_postfix[interpolation_method]}.tif"
            output_filename = os.path.splitext(os.path.basename(input_file))[0] + postfix
            output_file = os.path.join(output_dir, output_filename)
            assert os.path.isfile(output_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_dhm_multiprocessing()
