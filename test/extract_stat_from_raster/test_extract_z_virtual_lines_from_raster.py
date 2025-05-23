import logging
import os
import shutil
from pathlib import Path

import pytest
from hydra import compose, initialize

from produits_derives_lidar.extract_stat_from_raster import (
    extract_z_virtual_lines_from_raster,
)

TEST_PATH = Path(__file__).resolve().parent.parent
TMP_PATH = TEST_PATH / "tmp"

DATA_DIR = TEST_PATH / "data" / "bridge"
INPUT_RASTER_DIR = DATA_DIR / "mns_hydro_postfiltre"
INPUT_GEOMETRY_DIR = DATA_DIR / "input_operators/lignes_contraintes"
OUTPUT_DIR = TMP_PATH / "main_extract_z_virtual_lines_from_raster"
INPUT_VRT_PATH = OUTPUT_DIR / "MNS_HYDRO.vrt"


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.mkdir(TMP_PATH)


def test_extract_z_virtual_lines_from_raster_default():
    input_raster_dir = INPUT_RASTER_DIR
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    input_vrt_path = INPUT_VRT_PATH
    output_dir = OUTPUT_DIR
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.input_vrt_path={input_vrt_path}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)
    assert (Path(output_dir) / "constraint_lines.GeoJSON").is_file()


def test_extract_z_virtual_lines_from_raster_no_input_raster():
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    input_vrt_path = "MNS_HYDRO.vrt"
    output_dir = OUTPUT_DIR
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.input_vrt_path={input_vrt_path}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    with pytest.raises(ValueError):
        extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


def test_extract_z_virtual_lines_from_raster_no_input_geometry():
    input_raster_dir = INPUT_RASTER_DIR
    input_vrt_path = "MNS_HYDRO.vrt"
    output_dir = OUTPUT_DIR
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.input_vrt_path={input_vrt_path}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    with pytest.raises(ValueError):
        extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


def test_extract_z_virtual_lines_from_raster_no_output():
    input_raster_dir = INPUT_RASTER_DIR
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    input_vrt_path = "MNS_HYDRO.vrt"

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.input_vrt_path={input_vrt_path}",
                "extract_stat.output_dir=null",
                "extract_stat.output_geometry_filename=null",
            ],
        )
        with pytest.raises(ValueError, match="config.extract_stat.output_dir is empty"):
            extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_extract_z_virtual_lines_from_raster_default()
    # test_extract_z_virtual_lines_from_raster_no_input_geometry()
    # test_extract_z_virtual_lines_from_raster_no_input_raster()
    # test_extract_z_virtual_lines_from_raster_no_output()
