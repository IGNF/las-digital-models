import geopandas as gpd
import rasterio

from produits_derives_lidar.extract_stat_from_raster.rasters.clip_lines_by_raster import (
    clip_lines_to_raster,
)
from produits_derives_lidar.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    extract_min_z_from_mns_by_polylines,
)


def extract_z_virtual_lines_from_raster(
    input_geometry: str,
    input_raster: str,
    output_geometry: str,
    spatial_ref: str,
):
    """Extract Z value from raster by LIDAR tiles (tiling file)

    Args:
        input_geometry (str): Path to the input geometry file (GeoJSON or Shapefile) with 2D lines.
        input_raster (str): Path to the raster file by tile
        output_geometry (str): Path to save the output geometry file (GeoJSON or Shapefile)
        spatial_ref (str): CRS of the data.

    Raises:
        RuntimeError: If the input RASTER file has no valid EPSG code.
        ValueError: If no valid min Z value could be extracted for any geometry.
    """
    if not spatial_ref:
        with rasterio.open(input_raster) as src:
            spatial_ref = src.crs
        if spatial_ref is None:
            raise RuntimeError(f"RASTER file {input_raster} does not have a valid EPSG code.")

    # Read the input GeoJSON
    lines_gdf = gpd.read_file(input_geometry)

    if lines_gdf.crs is None:
        lines_gdf.set_crs(epsg=spatial_ref, inplace=True)

    if not all(lines_gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])):
        raise ValueError("Only LineString and MultiLineString geometries are supported.")

    # Clip lines by tile (raster and lidar)
    clipped_lines = clip_lines_to_raster(lines_gdf, input_raster, spatial_ref)

    if clipped_lines.empty:
        raise ValueError("No input geometry intersects the raster extent.")

    # Extract Z value from lines
    gdf_min_z = extract_min_z_from_mns_by_polylines(clipped_lines, input_raster)
    gdf_min_z = gdf_min_z.dropna(subset=["min_z"])  # Delete the lines without Zmin's value

    if gdf_min_z.empty:
        raise ValueError("All geometries returned None Zmin values; output will be empty.")

    gdf_min_z.to_file(output_geometry, driver="GeoJSON")
