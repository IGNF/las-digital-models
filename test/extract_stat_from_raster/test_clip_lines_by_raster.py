import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString

from produits_derives_lidar.extract_stat_from_raster.rasters.clip_lines_by_raster import (
    clip_lines_to_raster,
)

TEST_PATH = Path(__file__).resolve().parent.parent
DATA_RASTER_PATH = os.path.join(TEST_PATH, "data/bridge/mns_hydro_postfiltre")
INPUT_RASTER = os.path.join(DATA_RASTER_PATH, "test_mns_hydro_2023_0299_6802_LA93_IGN69_5m.tif")


def test_clip_3d_lines_to_raster():
    # Une ligne à l'intérieur de l'étendue du raster
    inside_line = LineString([(299950, 6801810), (299990, 6801820)])

    # Une ligne complètement en dehors de l’étendue du raster
    outside_line = LineString([(100000, 6600000), (100100, 6600100)])

    lines_gdf = gpd.GeoDataFrame(geometry=[inside_line, outside_line], crs="EPSG:2154")

    clipped = clip_lines_to_raster(lines_gdf, INPUT_RASTER)

    # Vérifie que seule la ligne à l'intérieur a été conservée
    assert len(clipped) == 1, f"Expected 1 clipped line, got {len(clipped)}"
    assert clipped.geometry.iloc[0].equals(inside_line), "The retained geometry is not the expected one"
