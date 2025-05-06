import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString

from produits_derives_lidar.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    extract_min_z_from_mns_by_polylines,
)

TEST_PATH = Path(__file__).resolve().parent.parent
DATA_RASTER_PATH = os.path.join(TEST_PATH, "data/bridge/mns_hydro_postfiltre")
INPUT_RASTER = os.path.join(DATA_RASTER_PATH, "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif")


def test_extract_min_z_from_mns_by_polylines():
    lines = [
        LineString(
            [(299934.058628972386941, 6801817.960626604966819), (300007.482969133299775, 6801822.184150597080588)]
        ),
        LineString(
            [(299922.471011867397465, 6801805.1817591432482), (299993.079669367230963, 6801808.322328265756369)]
        ),  # Ligne clairement en dehors de l’emprise du raster
    ]
    lines_gdf = gpd.GeoDataFrame(geometry=lines, crs="EPSG:2154")

    result = extract_min_z_from_mns_by_polylines(lines_gdf, INPUT_RASTER)

    # Check that all resulting geometries are LineStrings
    assert all(isinstance(geom, LineString) for geom in result.geometry)

    # Expected minimum Z values for each line, manually determined
    expected_min_z = [
        140.91,  # first line
        140.45,  # second line
    ]

    # Check that the computed min_z matches the expected ones
    for computed, expected in zip(result["min_z"], expected_min_z):
        assert computed == expected, f"Expected {expected}, but got {computed}"


def test_extract_min_z_with_geometry_outside_raster():
    outside_line = LineString([(100000.0, 6600000.0), (100010.0, 6600010.0)])
    lines_gdf = gpd.GeoDataFrame(geometry=[outside_line], crs="EPSG:2154")

    result = extract_min_z_from_mns_by_polylines(lines_gdf, INPUT_RASTER)
    assert result.empty, "Expected empty GeoDataFrame when line is outside raster"
