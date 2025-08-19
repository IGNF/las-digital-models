import logging
import os
import shutil
from pathlib import Path

import geopandas as gpd
import pytest
from hydra import compose, initialize
from shapely.geometry import LineString

from las_digital_models.extract_stat_from_raster import (
    extract_z_virtual_lines_from_raster,
)

TEST_PATH = Path(__file__).resolve().parent.parent
TMP_PATH = TEST_PATH / "tmp"

DATA_DIR = TEST_PATH / "data" / "bridge"
INPUT_RASTER_DIR = DATA_DIR / "mns_hydro_postfiltre"
INPUT_GEOMETRY_DIR = DATA_DIR / "input_operators/lignes_contraintes"
INPUT_CLIP_GEOMETRY_DIR = DATA_DIR / "input_operators/tabliers"
OUTPUT_DIR = TMP_PATH / "main_extract_z_virtual_lines_from_raster"
OUTPUT_VRT_FILENAME = "MNS_HYDRO.vrt"


def setup_module():
    try:
        shutil.rmtree(TMP_PATH)

    except FileNotFoundError:
        pass
    os.mkdir(TMP_PATH)


@pytest.mark.parametrize(
    "input_raster_dir, input_geometry_dir, input_clip_geometry_dir, input_geometry_filename, input_clip_geometry_filename",
    [
        (  # Standard values
            INPUT_RASTER_DIR, INPUT_GEOMETRY_DIR, INPUT_CLIP_GEOMETRY_DIR, 
            "NUALHD_1-0_DF_lignes_contrainte.geojson", "NUALHD_1-0_DF_tabliers_pont.geojson",
        ),
        (
            # Values where we multiLineString in past version
            TEST_PATH / "data" / "data_test_linestring", TEST_PATH / "data" / "data_test_linestring/", 
            TEST_PATH / "data" / "data_test_linestring/", 
            "lignes_contraintes.geojson", "ponts.geojson"
        ),
    ],
)
def test_extract_z_virtual_lines_from_raster_default(input_raster_dir, input_geometry_dir, input_clip_geometry_dir, 
                                                     input_geometry_filename, input_clip_geometry_filename):
    output_vrt_filename = OUTPUT_VRT_FILENAME
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
                f"extract_stat.input_clip_geometry_dir={input_clip_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.input_clip_geometry_filename={input_clip_geometry_filename}",
                f"extract_stat.output_vrt_filename={output_vrt_filename}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)
    assert (Path(output_dir) / "constraint_lines.GeoJSON").is_file()

    # Check geometry and Z value from output
    output_geometry_path = OUTPUT_DIR / output_geometry_filename
    gdf = gpd.read_file(output_geometry_path)
    assert not gdf.empty

    def is_linestring_z(geom):
        return isinstance(geom, LineString) and geom.has_z

    def all_z_coords_equal(geom):
        z_values = [coord[2] for coord in geom.coords]
        return all(z == z_values[0] for z in z_values)

    for geom in gdf.geometry:
        assert is_linestring_z(geom)  # the geometry's output is okay : LineString Z
        assert all_z_coords_equal(geom)  # this lines have the same Z value"


def test_extract_z_virtual_lines_from_raster_no_input_raster():
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_clip_geometry_dir = INPUT_CLIP_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    output_vrt_filename = OUTPUT_VRT_FILENAME
    output_dir = OUTPUT_DIR
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_clip_geometry_dir={input_clip_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.output_vrt_filename={output_vrt_filename}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    with pytest.raises(ValueError):
        extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


def test_extract_z_virtual_lines_from_raster_no_input_geometry():
    input_raster_dir = INPUT_RASTER_DIR
    output_vrt_filename = OUTPUT_VRT_FILENAME
    output_dir = OUTPUT_DIR
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.output_vrt_filename={output_vrt_filename}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    with pytest.raises(ValueError):
        extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


def test_extract_z_virtual_lines_from_raster_no_output():
    input_raster_dir = INPUT_RASTER_DIR
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_clip_geometry_dir = INPUT_CLIP_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    output_vrt_filename = OUTPUT_VRT_FILENAME

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_clip_geometry_dir={input_clip_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.output_vrt_filename={output_vrt_filename}",
                "extract_stat.output_dir=null",
                "extract_stat.output_geometry_filename=null",
            ],
        )
        with pytest.raises(ValueError, match="config.extract_stat.output_dir is empty"):
            extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)


def test_extract_z_virtual_lines_from_raster_outside():
    input_raster_dir = INPUT_RASTER_DIR
    input_geometry_dir = INPUT_GEOMETRY_DIR
    input_clip_geometry_dir = INPUT_CLIP_GEOMETRY_DIR
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte_outside_MNS.geojson"
    input_clip_geometry_filename = "NUALHD_1-0_DF_tabliers_pont.geojson"
    output_vrt_filename = OUTPUT_VRT_FILENAME
    output_dir = TMP_PATH / "main_extract_z_virtual_lines_from_raster_outside"
    output_geometry_filename = "constraint_lines.GeoJSON"
    os.makedirs(output_dir, exist_ok=True)

    with initialize(version_base="1.2", config_path="../../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="config",
            overrides=[
                f"extract_stat.input_raster_dir={input_raster_dir}",
                f"extract_stat.input_geometry_dir={input_geometry_dir}",
                f"extract_stat.input_clip_geometry_dir={input_clip_geometry_dir}",
                f"extract_stat.input_geometry_filename={input_geometry_filename}",
                f"extract_stat.input_clip_geometry_filename={input_clip_geometry_filename}",
                f"extract_stat.output_vrt_filename={output_vrt_filename}",
                f"extract_stat.output_dir={output_dir}",
                f"extract_stat.output_geometry_filename={output_geometry_filename}",
            ],
        )
    with pytest.raises(ValueError, match="All geometries returned None. Abort."):
        extract_z_virtual_lines_from_raster.run_extract_z_virtual_lines_from_raster(cfg)

    assert not (Path(output_dir) / "constraint_lines.GeoJSON").is_file()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_extract_z_virtual_lines_from_raster_default()
    test_extract_z_virtual_lines_from_raster_no_input_geometry()
    test_extract_z_virtual_lines_from_raster_no_input_raster()
    test_extract_z_virtual_lines_from_raster_no_output()
