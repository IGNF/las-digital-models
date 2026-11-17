import os
from pathlib import Path

import geopandas as gpd
import pytest
from hydra import compose, initialize
from shapely.geometry import LineString

from las_digital_models.extract_stat_from_raster import (
    extract_z_virtual_lines_from_raster,
)


@pytest.fixture(scope="module")
def output_vrt_filename():
    return "MNS_HYDRO.vrt"


@pytest.fixture(scope="module")
def tmp_path(base_tmp_path):
    return base_tmp_path / "extract_stat_from_raster" / "extract_z_virtual_lines_from_raster"


@pytest.fixture(scope="module")
def test_data(base_data_path):
    return {
        "default": {
            "input_raster_dir": base_data_path / "bridge" / "mns_hydro_postfiltre",
            "input_geometry_dir": base_data_path / "bridge" / "input_operators/lignes_contraintes",
            "input_clip_geometry_dir": base_data_path / "bridge" / "input_operators/tabliers",
            "input_geometry_filename": "NUALHD_1-0_DF_lignes_contrainte.geojson",
            "input_clip_geometry_filename": "NUALHD_1-0_DF_tabliers_pont.geojson",
        },
        "multilineString": {  # Values where we multiLineString in past version
            "input_raster_dir": base_data_path / "data_test_linestring",
            "input_geometry_dir": base_data_path / "data_test_linestring",
            "input_clip_geometry_dir": base_data_path / "data_test_linestring",
            "input_geometry_filename": "lignes_contraintes.geojson",
            "input_clip_geometry_filename": "ponts.geojson",
        },
    }


@pytest.mark.parametrize("test_case", ["default", "multilineString"])
def test_extract_z_virtual_lines_from_raster_default(test_data, test_case, output_vrt_filename, tmp_path):
    input_raster_dir = test_data[test_case]["input_raster_dir"]
    input_geometry_dir = test_data[test_case]["input_geometry_dir"]
    input_clip_geometry_dir = test_data[test_case]["input_clip_geometry_dir"]
    input_geometry_filename = test_data[test_case]["input_geometry_filename"]
    input_clip_geometry_filename = test_data[test_case]["input_clip_geometry_filename"]
    output_dir = tmp_path / "test_extract_z_virtual_lines_from_raster_default"
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
    output_geometry_path = output_dir / output_geometry_filename
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


def test_extract_z_virtual_lines_from_raster_no_input_raster(tmp_path, test_data, output_vrt_filename):
    input_geometry_dir = test_data["default"]["input_geometry_dir"]
    input_clip_geometry_dir = test_data["default"]["input_clip_geometry_dir"]
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"
    output_dir = tmp_path / "test_extract_z_virtual_lines_from_raster_no_input_raster"
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


def test_extract_z_virtual_lines_from_raster_no_input_geometry(tmp_path, test_data, output_vrt_filename):
    input_raster_dir = test_data["default"]["input_raster_dir"]
    output_dir = tmp_path / "test_extract_z_virtual_lines_from_raster_no_input_geometry"
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


def test_extract_z_virtual_lines_from_raster_no_output(test_data, output_vrt_filename):
    input_raster_dir = test_data["default"]["input_raster_dir"]
    input_geometry_dir = test_data["default"]["input_geometry_dir"]
    input_clip_geometry_dir = test_data["default"]["input_clip_geometry_dir"]
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte.shp"

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


def test_extract_z_virtual_lines_from_raster_outside(tmp_path, test_data, output_vrt_filename):
    input_raster_dir = test_data["default"]["input_raster_dir"]
    input_geometry_dir = test_data["default"]["input_geometry_dir"]
    input_clip_geometry_dir = test_data["default"]["input_clip_geometry_dir"]
    input_geometry_filename = "NUALHD_1-0_DF_lignes_contrainte_outside_MNS.geojson"
    input_clip_geometry_filename = "NUALHD_1-0_DF_tabliers_pont.geojson"
    output_dir = tmp_path / "test_extract_z_virtual_lines_from_raster_outside"
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
