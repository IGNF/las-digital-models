import logging
import os
import subprocess as sp

import pytest

from las_digital_models.commons import commons

pixel_size = 0.5


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    return base_tmp_path / "run_script"


@pytest.fixture(scope="module")
def expected_output_dirs(tmp_path):
    return {
        "dtm": os.path.join(tmp_path, "DTM"),
        "dsm": os.path.join(tmp_path, "DSM"),
        "dhm": os.path.join(tmp_path, "DHM"),
    }


@pytest.mark.functional_test
def test_run_script(tmp_path, base_data_path, expected_output_dirs):
    cmd = ["./run.sh", "-i", base_data_path, "-o", tmp_path, "-p", str(pixel_size), "-c", "test"]
    print(cmd)
    r = sp.run(cmd, capture_output=True)
    logging.debug(f"Stdout is: {r.stdout.decode()}")
    logging.debug(f"Stderr is: {r.stderr.decode()}")
    if r.returncode == 1:
        msg = r.stderr.decode()

        pytest.fail(f"Test for run.sh failed with message: {msg}", True)

    # Check that all files are created (for all methods)

    for input_file in os.listdir(base_data_path):
        if input_file.endswith(("las", "laz")):
            tilename = os.path.splitext(input_file)[0]
            for od in expected_output_dirs.keys():
                _size = commons.give_name_resolution_raster(pixel_size)
                out_filename = f"{tilename}{_size}.tif"
                out_path = os.path.join(expected_output_dirs[od], out_filename)
                assert os.path.isfile(out_path), f"Output for {od} was not generated"
