import argparse

import geopandas as gpd
from pdaltools.add_points_in_pointcloud import clip_3d_lines_to_tile
from pdaltools.las_info import get_epsg_from_las

from produits_derives_lidar.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    extract_min_z_from_mns_by_polylines,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser("Add points from GeoJSON in LIDAR tile")
    parser.add_argument(
        "--input_geometry", "-ig", type=str, required=True, help="Input Geometry file (GeoJSON or Shapefile)"
    )
    parser.add_argument("--input_las", "-i", type=str, required=True, help="Input las file")
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
    parser.add_argument(
        "--tile_width",
        type=int,
        default=1000,
        help="width of tiles in meters",
    )

    return parser.parse_args(argv)


def extract_z_virtual_lines_from_raster_by_las(
    input_geometry: str,
    input_las: str,
    input_raster: str,
    output_geometry: str,
    spatial_ref: str,
    tile_width: int,
):
    """Extract Z value from raster by LIDAR tiles (tiling file)

    Args:
        input_geometry (str): Path to the input geometry file (GeoJSON or Shapefile) with 2D lines.
        input_las (str): Path to the LIDAR `.las/.laz` file by tile.
        input_raster (str): Path to the raster file by tile
        output_geometry (str): Path to save the output geometry file (GeoJSON or Shapefile)
        spatial_ref (str): CRS of the data.
        tile_width (int): Width of the tile in meters (default: 1000).

    Raises:
        RuntimeError: If the input LAS file has no valid EPSG code.
        ValueError: Unsupported geometry type in the input Geometry file
    """
    if not spatial_ref:
        spatial_ref = get_epsg_from_las(input_las)
        if spatial_ref is None:
            raise RuntimeError(f"LAS file {input_las} does not have a valid EPSG code.")

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
        gdf = clip_3d_lines_to_tile(gdf, input_las, spatial_ref, tile_width)
        # Extract Z value from lines
        gdf_min_z = extract_min_z_from_mns_by_polylines(gdf, input_raster)
        gdf_min_z.to_file(output_geometry, driver="GeoJSON")
    else:
        raise ValueError("Unsupported geometry type in the input Geometry file.")


if __name__ == "__main__":
    args = parse_args()
    extract_z_virtual_lines_from_raster_by_las(**vars(args))
