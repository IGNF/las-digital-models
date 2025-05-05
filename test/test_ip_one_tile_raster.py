import logging
import os
import shutil
from pathlib import Path

import pytest
from hydra import compose, initialize

from produits_derives_lidar import ip_one_tile_raster

TEST_PATH = Path(__file__).resolve().parent
TMP_PATH = TEST_PATH / "tmp"

DATA_DIR = TEST_PATH / "data" / "bridge"
INPUT_RASTER_DIR = DATA_DIR / "mns_hydro_postfiltre"
INPUT_GEOMETRY_DIR = DATA_DIR / "input_operators/lignes_contraintes"
OUTPUT_DIR = TMP_PATH / "main_ip_one_tile_raster"


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.mkdir(TMP_PATH)


def test_ip_one_tile_raster_default():
    input_raster_dir = INPUT_RASTER_DIR
    input_raster_filename = "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif"
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"io.input_raster_dir={input_raster_dir}",
                f"io.input_raster_filename={input_raster_filename}",
                f"io.input_geometry_dir={input_geometry_dir}",
                f"io.input_geometry_filename={input_geometry_filename}",
                f"io.output_dir={output_dir}",
            ],
        )
    ip_one_tile_raster.run_ip_on_tile_raster(cfg)
    assert (Path(output_dir) / "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m_lines.GeoJSON").is_file()


def test_ip_one_tile_raster_no_input_raster():
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"io.input_geometry_dir={input_geometry_dir}",
                f"io.input_geometry_filename={input_geometry_filename}",
                f"io.output_dir={output_dir}",
            ],
        )
    with pytest.raises(ValueError):
        ip_one_tile_raster.run_ip_on_tile_raster(cfg)


def test_ip_one_tile_raster_no_input_geometry():
    input_raster_dir = INPUT_RASTER_DIR
    input_raster_filename = "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif"
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"io.input_raster_dir={input_raster_dir}",
                f"io.input_raster_filename={input_raster_filename}",
                f"io.output_dir={output_dir}",
            ],
        )
    with pytest.raises(ValueError):
        ip_one_tile_raster.run_ip_on_tile_raster(cfg)


def test_ip_one_tile_raster_no_output():
    input_raster_dir = INPUT_RASTER_DIR
    input_raster_filename = "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif"
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"io.input_raster_dir={input_raster_dir}",
                f"io.input_raster_filename={input_raster_filename}",
                f"io.input_geometry_dir={input_geometry_dir}",
                f"io.input_geometry_filename={input_geometry_filename}",
                "io.output_dir=null",
            ],
        )
        with pytest.raises(ValueError, match="config.io.output_dir is empty"):
            ip_one_tile_raster.run_ip_on_tile_raster(cfg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile_raster_default()
    test_ip_one_tile_raster_no_input_geometry()
    test_ip_one_tile_raster_no_input_raster()
    test_ip_one_tile_raster_no_output()
