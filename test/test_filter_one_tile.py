from produit_derive_lidar import filter_one_tile
import logging
import os
import pytest
import shutil
import test.utils.point_cloud_utils as pcu
from hydra import initialize, compose


coordX = 77055
coordY = 627760

test_path = os.path.dirname(__file__)
tmp_path = os.path.join(test_path, "tmp")

expected_output_nb_points_ground = 22343
expected_output_nb_points_building = 14908


output_dir = os.path.join(tmp_path,  "ground")

output_default_file = os.path.join(output_dir, f"test_data_{coordX}_{coordY}_LA93_IGN69.laz")

output_las_file = os.path.join(output_dir,f"test_data_{coordX}_{coordY}_LA93_IGN69.las")


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def test_filter_one_tile():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                      overrides=["io=test", "tile_geometry=test",
                                 f"io.output_dir={output_dir}",
                                 f"filter=default_test"])

    filter_one_tile.run_filter_on_tile(cfg)
    assert os.path.isfile(output_default_file)
    assert pcu.get_nb_points(output_default_file) == expected_output_nb_points_ground


def test_filter_one_tile_building_class():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                      overrides=["io=test", "tile_geometry=test",
                                 f"io.output_dir={output_dir}",
                                  f"filter.keep_classes=[6]"])
    filter_one_tile.run_filter_on_tile(cfg)
    assert os.path.isfile(output_default_file)
    assert pcu.get_nb_points(output_default_file) == expected_output_nb_points_building


def test_filter_one_tile_force_output():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                        overrides=["io=test", "tile_geometry=test",
                                    f"io.output_dir={output_dir}",
                                    f"filter=default_test",
                                    "io.forced_intermediate_ext=las"])
    filter_one_tile.run_filter_on_tile(cfg)
    assert os.path.isfile(output_las_file)
    assert pcu.get_nb_points(output_las_file) == expected_output_nb_points_ground


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_filter_one_tile()
    test_filter_one_tile_building_class()
