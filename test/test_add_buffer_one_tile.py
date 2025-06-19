import logging
import os
import shutil
import test.utils.point_cloud_utils as pcu

from hydra import compose, initialize

from las_digital_models import add_buffer_one_tile

TEST_PATH = os.path.dirname(__file__)
TMP_PATH = os.path.join(TEST_PATH, "tmp/buffer")
DATA_PATH = os.path.join(TEST_PATH, "data")


def setup_module(module):
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.makedirs(TMP_PATH, exist_ok=True)


def test_add_buffer_one_tile():
    # DATA_PATH contains a .laz file, but check that the io.forced_intermediate_ext parameter forces to look for a
    # .laz file
    input_filename = "test_data_77055_627760_LA93_IGN69.las"
    output_filename = "test_data_77055_627760_LA93_IGN69.laz"
    output_file = os.path.join(TMP_PATH, output_filename)

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                f"io.input_dir={DATA_PATH}",
                f"io.input_filename={input_filename}",
                "io.forced_intermediate_ext=laz",
                f"io.output_dir={TMP_PATH}",
                "buffer=test",
            ],
        )

    add_buffer_one_tile.run_add_buffer_one_tile(cfg)
    assert os.path.isfile(output_file)
    logging.info(pcu.get_nb_points(output_file))
    assert pcu.get_nb_points(output_file) == 103359
    assert pcu.get_classification_values(output_file) == {1, 2, 3, 4, 5, 6, 64}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_add_buffer_one_tile()
