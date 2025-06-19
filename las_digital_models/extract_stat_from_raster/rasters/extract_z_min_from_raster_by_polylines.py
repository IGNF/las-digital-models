import logging

import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
from shapely.geometry import LineString, box


def clip_lines_by_raster(input_lines: gpd.GeoDataFrame, input_raster: str, crs: str = None) -> gpd.GeoDataFrame:
    """
    Select lines from a GeoDataFrame that intersect the raster extent.

    Args:
        input_lines (gpd.GeoDataFrame): GeoDataFrame with lines.
        input_raster (str): Path to the raster file (e.g., .tif).
        crs (str, optional): Target CRS if reprojection is needed.

    Returns:
        gpd.GeoDataFrame: Lines that intersect with the raster extent.
    """
    # Open the raster and get its bounding box
    with rasterio.open(input_raster) as src:
        bounds = src.bounds
        raster_crs = src.crs

    # Convert lines to raster CRS if needed
    input_lines = input_lines.to_crs(crs if crs else raster_crs)
    bbox_polygon = box(*bounds)

    # Select lines that intersect the raster bbox
    clipped_lines = input_lines[input_lines.intersects(bbox_polygon)]

    return clipped_lines


def extract_polylines_min_z_from_dsm(
    lines_gdf: gpd.GeoDataFrame, dsm_rasterpath: str, no_data_value: int = 9999
) -> gpd.GeoDataFrame:
    """
    Extracts the minimum Z value from a DSM raster for each polyline (LineString or MultiLineString)
    in the input shapefile, keeping the original geometry.

    Args:
        lines_gdf (str): GeoDataFrame with 2D lines.
        dsm_rasterpath (str): Path to the DSM raster (.vrt).
        no_data_value (int): no data value (default to -9999)

    Returns:
        GeoDataFrame: A GeoDataFrame with generated 3D Lines.
    """

    def get_z_min_on_linestring(geom, dsm_rasterpath):
        if isinstance(geom, LineString):
            stats = zonal_stats(
                vectors=[geom], raster=dsm_rasterpath, stats=["min"], all_touched=True, nodata=no_data_value
            )
            min_z = stats[0]["min"]

            if min_z is None or int(min_z) == no_data_value:
                logging.warning(f"No valid Zmin found for geometry {geom} (ignored).")
                return None

            coords_3d = [(x, y, round(min_z, 2)) for x, y in geom.coords]
            return LineString(coords_3d)

        else:
            logging.warning(f"Geometry {geom} is not a LineString (ignored).")
            return None

    # Apply this function "get_z_min in linestring"
    lines_gdf["geometry"] = lines_gdf["geometry"].apply(lambda geom: get_z_min_on_linestring(geom, dsm_rasterpath))

    def is_invalid(geom):
        if geom is None:
            return True
        if isinstance(geom, LineString) and geom.has_z:
            z_vals = [pt[2] for pt in geom.coords]
            return all(z == no_data_value for z in z_vals)
        return False

    lines_gdf = lines_gdf[~lines_gdf["geometry"].apply(is_invalid)]

    return lines_gdf
