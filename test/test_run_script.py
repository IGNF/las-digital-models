import logging
import os
import shutil
import subprocess as sp

import pytest

from las_digital_models.commons import commons

test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
input_dir = os.path.join(test_path, "data")
output_dir = os.path.join(tmp_path, "output_run_script")
file_ext = "laz"
pixel_size = 0.5

expected_output_dirs = {
    "dtm": os.path.join(output_dir, "DTM"),
    "dsm": os.path.join(output_dir, "DSM"),
    "dhm": os.path.join(output_dir, "DHM"),
}


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except FileNotFoundError:
        pass
    os.mkdir(tmp_path)


@pytest.mark.functional_test
def test_run_script():
    cmd = ["./run.sh", "-i", input_dir, "-o", output_dir, "-p", str(pixel_size), "-c", "test"]
    print(cmd)
    r = sp.run(cmd, capture_output=True)
    logging.debug(f"Stdout is: {r.stdout.decode()}")
    logging.debug(f"Stderr is: {r.stderr.decode()}")
    if r.returncode == 1:
        msg = r.stderr.decode()

        pytest.fail(f"Test for run.sh failed with message: {msg}", True)

    # Check that all files are created (for all methods)

    for input_file in os.listdir(input_dir):
        if input_file.endswith(("las", "laz")):
            tilename = os.path.splitext(input_file)[0]
            for od in expected_output_dirs.keys():
                _size = commons.give_name_resolution_raster(pixel_size)
                out_filename = f"{tilename}{_size}.tif"
                out_path = os.path.join(expected_output_dirs[od], out_filename)
                assert os.path.isfile(out_path), f"Output for {od} was not generated"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_run_script()
