import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString

from produits_derives_lidar.extract_stat_from_raster import (
    extract_z_virtual_lines_from_raster,
)

TEST_PATH = Path(__file__).resolve().parent.parent

TMP_PATH = os.path.join(TEST_PATH, "tmp/extract_z_virtual_lines_from_raster")
DATA_RASTER_PATH = os.path.join(TEST_PATH, "data/bridge/mns_hydro_postfiltre")
DATA_LINES_PATH = os.path.join(TEST_PATH, "data/bridge/input_operators/lignes_contraintes")

INPUT_RASTER = os.path.join(DATA_RASTER_PATH, "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif")
INPUT_LINES = os.path.join(DATA_LINES_PATH, "NUALHD_1-0_DF_lignes_contrainte.shp")

OUTPUT_LINES = os.path.join(TMP_PATH, "test_lines_2023_0299_6802_LA93_IGN69.geojson")


def setup_module(module):
    os.makedirs(TMP_PATH, exist_ok=True)


def test_extract_z_virtual_lines_from_raster_by_las():
    # Ensure the output file doesn't exist before the test
    if Path(OUTPUT_LINES).exists():
        os.remove(OUTPUT_LINES)

    extract_z_virtual_lines_from_raster.extract_z_virtual_lines_from_raster(
        INPUT_LINES, INPUT_RASTER, OUTPUT_LINES, "EPSG:2154"
    )

    lines_result = gpd.read_file(OUTPUT_LINES)

    # Check that all resulting geometries are LineStrings
    assert all(isinstance(geom, LineString) for geom in lines_result.geometry)

    # Check return 2 lines for the tile LIDAR
    assert len(lines_result) == 2

    # Check the result is correct
    expected = [
        {
            "geometry": LineString([(299934.0586289724, 6801817.960626605), (300007.4829691333, 6801822.184150597)]),
            "min_z": 140.91,
        },
        {
            "geometry": LineString([(299922.4710118674, 6801805.181759143), (299993.0796693672, 6801808.322328266)]),
            "min_z": 140.45,
        },
    ]
    for idx, expected in enumerate(expected):
        result_geom = lines_result.iloc[idx].geometry
        result_min_z = lines_result.iloc[idx]["min_z"]

        # Strict comparison of geometry
        assert result_geom.equals_exact(expected["geometry"], tolerance=1e-6)

        # Strict comparison of min_z
        assert result_min_z == expected["min_z"]
