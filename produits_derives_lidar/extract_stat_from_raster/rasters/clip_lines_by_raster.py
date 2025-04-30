import geopandas as gpd
import rasterio
from shapely.geometry import box


def clip_lines_to_raster(input_lines: gpd.GeoDataFrame, input_raster: str, crs: str = None) -> gpd.GeoDataFrame:
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
    if crs:
        input_lines = input_lines.to_crs(crs)
        bbox_polygon = box(*bounds)
    else:
        input_lines = input_lines.to_crs(raster_crs)
        bbox_polygon = box(*bounds)

    # Select lines that intersect the raster bbox
    clipped_lines = input_lines[input_lines.intersects(bbox_polygon)]

    return clipped_lines
