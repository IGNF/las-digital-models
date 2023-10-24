import logging
import os
import shutil
import test.utils.point_cloud_utils as pcu

from hydra import compose, initialize

from produits_derives_lidar import add_buffer_one_tile

coordX = 77055
coordY = 627760

test_path = os.path.dirname(__file__)
tmp_path = os.path.join(test_path, "tmp")

expected_output_nb_points = 47037


output_dir = os.path.join(tmp_path, "buffer")

output_default_file = os.path.join(output_dir, f"test_data_{coordX}_{coordY}_LA93_IGN69.las")

output_las_file = os.path.join(output_dir, f"test_data_{coordX}_{coordY}_LA93_IGN69.las")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except FileNotFoundError:
        pass
    os.mkdir(tmp_path)


def test_add_buffer_one_tile():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                "io=test",
                "tile_geometry=test",
                "io.input_dir=./test/data/ground",
                "io.forced_intermediate_ext=las",
                f"io.output_dir={output_dir}",
                "buffer=test",
            ],
        )

    add_buffer_one_tile.run_add_buffer_one_tile(cfg)
    assert os.path.isfile(output_default_file)
    logging.info(pcu.get_nb_points(output_default_file))
    assert pcu.get_nb_points(output_default_file) == expected_output_nb_points


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_add_buffer_one_tile()
