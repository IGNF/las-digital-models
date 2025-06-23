from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import LineString

from las_digital_models.extract_stat_from_raster.vectors.clip_geometry import (
    clip_lines_by_polygons,
)

TEST_PATH = Path(__file__).resolve().parent.parent

TMP_PATH = TEST_PATH / "tmp"

DATA_DIR = TEST_PATH / "data" / "bridge" / "input_operators"
DATA_LINES = DATA_DIR / "lignes_contraintes/test_constraint_lines_3D_OE.geojson"
DATA_LINES_OUTSIDE = DATA_DIR / "lignes_contraintes/test_constraint_lines_3D_OE_outside.geojson"
DATA_BRIDGES = DATA_DIR / "tabliers/test_tabliers_pont_OE.geojson"


def test_create_hydro_vector_mask_default():
    # Parameters
    crs = CRS.from_epsg(2154)
    lines_gdf = gpd.read_file(DATA_LINES)
    bridges_gdf = gpd.read_file(DATA_BRIDGES)

    gdf = clip_lines_by_polygons(lines_gdf, bridges_gdf)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, LineString) for geom in gdf.geometry)  # All geometry should LineString

    expected_number_of_geometries = 6
    assert len(gdf) == expected_number_of_geometries  # Six geometry

    # Define expected geometries
    expected_geometries = [
        LineString([(857170.91, 6856275.22, 177.24), (857192.69, 6856277.59, 177.24)]),
        LineString([(857200.29, 6856278.84, 177.24), (857228.21, 6856284.42, 177.24)]),
        LineString([(857188.43, 6856290.58, 177.93), (857219.86, 6856294.14, 177.93)]),
        LineString([(857190.83, 6856288.48, 177.93), (857220.02, 6856292.22, 177.93)]),
        LineString([(857139.26, 6856297.25, 177.25), (857174.66, 6856290.19, 177.25)]),
        LineString([(857193.85, 6856285.83, 177.25), (857225.12, 6856287.22, 177.25)]),
    ]

    # Check geometries are exactly the expected ones
    def round_linestring_coords(ls, ndigits=2):
        return LineString([(round(x, ndigits), round(y, ndigits), round(z, ndigits)) for x, y, z in ls.coords])

    actual_geoms = [round_linestring_coords(geom) for geom in gdf.geometry]

    for expected_geom in expected_geometries:
        assert any(
            expected_geom.equals(actual_geom) for actual_geom in actual_geoms
        ), f"Expected geometry not found: {expected_geom.wkt}"


def test_create_hydro_vector_mask_outside():
    # Parameters
    lines_outsides_gdf = gpd.read_file(DATA_LINES_OUTSIDE)
    bridges_gdf = gpd.read_file(DATA_BRIDGES)

    gdf = clip_lines_by_polygons(lines_outsides_gdf, bridges_gdf)

    assert gdf.empty  # GeoDataFrame should empty
