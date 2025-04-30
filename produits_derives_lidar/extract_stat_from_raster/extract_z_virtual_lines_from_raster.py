import argparse

import geopandas as gpd
import rasterio

from produits_derives_lidar.extract_stat_from_raster.rasters.clip_lines_by_raster import (
    clip_lines_to_raster,
)
from produits_derives_lidar.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    extract_min_z_from_mns_by_polylines,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser("Add points from GeoJSON in LIDAR tile")
    parser.add_argument(
        "--input_geometry", "-ig", type=str, required=True, help="Input Geometry file (GeoJSON or Shapefile)"
    )
    parser.add_argument("--input_raster", "-r", type=str, required=True, help="Input raster file")
    parser.add_argument(
        "--output_geometry",
        "-o",
        type=str,
        required=True,
        default="",
        help="Output eometry file (GeoJSON or Shapefile)",
    )
    parser.add_argument(
        "--spatial_ref",
        type=str,
        required=False,
        help="spatial reference for the writer",
    )

    return parser.parse_args(argv)


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
        ValueError: Unsupported geometry type in the input Geometry file
    """
    if not spatial_ref:
        with rasterio.open(input_raster) as src:
            spatial_ref = src.crs
        if spatial_ref is None:
            raise RuntimeError(f"RASTER file {input_raster} does not have a valid EPSG code.")

    # Read the input GeoJSON
    gdf = gpd.read_file(input_geometry)

    if gdf.crs is None:
        gdf.set_crs(epsg=spatial_ref, inplace=True)

    # Store the unique geometry type in a variable
    unique_geom_type = gdf.geometry.geom_type.unique()

    # Check the geometry type
    if len(unique_geom_type) != 1:
        raise ValueError("Several geometry types found in geometry file. This case is not handled.")

    if unique_geom_type in ["LineString", "MultiLineString"]:
        gdf = gdf.explode(index_parts=False).reset_index(drop=True)
        # Clip lines by tile (raster and lidar)
        gdf = clip_lines_to_raster(gdf, input_raster, spatial_ref)
        # Extract Z value from lines
        gdf_min_z = extract_min_z_from_mns_by_polylines(gdf, input_raster)
        gdf_min_z.to_file(output_geometry, driver="GeoJSON")
    else:
        raise ValueError("Unsupported geometry type in the input Geometry file.")


if __name__ == "__main__":
    args = parse_args()
    extract_z_virtual_lines_from_raster(**vars(args))
