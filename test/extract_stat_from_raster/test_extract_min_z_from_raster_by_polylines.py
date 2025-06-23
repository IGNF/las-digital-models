import os
from pathlib import Path

import geopandas as gpd
import pytest
import rasterio
from shapely.geometry import LineString

from las_digital_models.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    clip_lines_by_raster,
    extract_polylines_min_z_from_dsm,
)

TEST_PATH = Path(__file__).resolve().parent.parent
DATA_RASTER_PATH = os.path.join(TEST_PATH, "data/bridge/mns_hydro_postfiltre")
INPUT_RASTER = os.path.join(DATA_RASTER_PATH, "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif")


def test_extract_polylines_min_z_from_dsm():
    lines = [
        LineString([(299934.06, 6801817.96), (300007.48, 6801822.18)]),
        LineString([(299922.47, 6801805.18), (299993.08, 6801808.32)]),  # Line outside from raster
    ]
    lines_gdf = gpd.GeoDataFrame(geometry=lines, crs="EPSG:2154")

    result = extract_polylines_min_z_from_dsm(lines_gdf, INPUT_RASTER)

    # # Check that all resulting geometries are LineStrings
    assert all(isinstance(geom, LineString) for geom in result.geometry)
    assert all(geom.has_z for geom in result.geometry)

    # Expected minimum Z values for each line, manually determined
    expected_min_z = [
        140.91,  # first line
        140.45,  # second line
    ]

    # Check that the computed min_z matches the expected ones
    for geom, expected_z in zip(result.geometry, expected_min_z):
        zs = [round(z, 2) for x, y, z in geom.coords]
        assert all(z == expected_z for z in zs), f"Expected all Z = {expected_z}, got {zs}"


def test_line_outside_raster():
    line = LineString([(0, 0), (1, 1)])  # no intersection with raster footprint
    lines_gdf = gpd.GeoDataFrame(geometry=[line], crs="EPSG:2154")

    result = extract_polylines_min_z_from_dsm(lines_gdf, INPUT_RASTER)

    assert len(result) == 0


@pytest.fixture(scope="module")
def raster_bounds():
    with rasterio.open(INPUT_RASTER) as src:
        return src.bounds  # left, bottom, right, top


@pytest.mark.parametrize(
    "line_type, line_geom, should_be_retained",
    [
        ("inside_line", lambda b: LineString([(b.left + 10, b.bottom + 10), (b.left + 50, b.bottom + 50)]), True),
        (
            "outside_line",
            lambda b: LineString([(b.left - 1000, b.bottom - 1000), (b.left - 900, b.bottom - 900)]),
            False,
        ),
        ("edge_line", lambda b: LineString([(b.left, b.bottom + 10), (b.left, b.top - 10)]), True),
        ("touching_line", lambda b: LineString([(b.right - 1, b.top - 1), (b.right + 500, b.top + 500)]), True),
        (
            "crossing_line",
            lambda b: LineString([(b.left - 50, (b.bottom + b.top) / 2), (b.right + 50, (b.bottom + b.top) / 2)]),
            True,
        ),
    ],
)
def test_clip_lines_parametrized(raster_bounds, line_type, line_geom, should_be_retained):
    line = line_geom(raster_bounds)
    lines_gdf = gpd.GeoDataFrame(geometry=[line], crs="EPSG:2154")

    clipped = clip_lines_by_raster(lines_gdf, INPUT_RASTER)

    if should_be_retained:
        assert not clipped.empty, f"{line_type} should have been retained"
        assert clipped.geometry.intersects(line).any(), f"{line_type} not properly clipped"
    else:
        assert clipped.empty, f"{line_type} should NOT have been retained"
