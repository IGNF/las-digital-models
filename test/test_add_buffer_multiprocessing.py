import logging
import numpy as np
import os
import pytest
import shutil
from produit_derive_lidar.add_buffer_multiprocessing import start_pool



test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
input_dir = os.path.join(test_path, "data")

spatial_reference = "EPSG:2154"
output_dir = tmp_path
buffer_width = 10

def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_add_buffer_multiprocessing():
    filetype = "laz"
    # Create the severals folder if not exists
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(tmp_path, exist_ok=True)
    start_pool(input_dir=input_dir,
               output_dir=output_dir,
               buffer_width=buffer_width,
               filetype=filetype
    )
    # Check all files are generated
    for input_file in os.listdir(input_dir):
        if input_file.endswith(filetype):
            output_filename =os.path.basename(input_file)
            output_file = os.path.join(output_dir, output_filename)
            assert os.path.isfile(output_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_add_buffer_multiprocessing()