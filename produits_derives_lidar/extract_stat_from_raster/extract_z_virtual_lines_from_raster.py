"""
Main script to run the extraction of minimum Z values along lines (defined in a geometry file) \
from raster containing Z value
"""
import logging
import os

import geopandas as gpd
import hydra
from omegaconf import DictConfig
from osgeo import gdal

from produits_derives_lidar.commons import commons
from produits_derives_lidar.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    clip_lines_by_raster,
    extract_polylines_min_z_from_dsm,
)

gdal.UseExceptions()

log = commons.get_logger(__name__)


def create_list_raster_and_vrt(raster_dir: str, output_vrt: str):
    """Create list of input's raster and vrt

    Args:
        raster_dir (str): Directory containing .tif files (MNS raster).
        output_vrt (str): Path to the output VRT file.

    Raises:
        ValueError: If the list of input RASTER file doesn't exist
        ValueError: If the VRT doesn't create
    """
    dir_list_raster = [os.path.join(raster_dir, f) for f in os.listdir(raster_dir) if f.lower().endswith(".tif")]
    if not dir_list_raster:
        raise ValueError(f"No raster (.tif) files found in {raster_dir}")

    # Build and save VRT file
    vrt_options = gdal.BuildVRTOptions(resampleAlg="cubic", addAlpha=True)
    my_vrt = gdal.BuildVRT(output_vrt, dir_list_raster, options=vrt_options)

    if my_vrt is None:
        raise ValueError(f"gdal.BuildVRT returned None for {output_vrt}")

    my_vrt = None  # necessary to close the VRT file properly


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_extract_z_virtual_lines_from_raster(config: DictConfig):
    """Extract the minimum Z value along one or more 2d lines (contained in a geometry file) using hydra config
    config parameters are explained in the default.yaml files

    Raises:
        RuntimeError: If the input RASTER file has no valid EPSG code.
        ValueError: if the geometry file does not only contain (Multi)LineStrings.
    """
    # Check input files
    raster_dir = config.extract_stat.input_raster_dir
    if not os.path.isdir(raster_dir):
        raise ValueError("""config.extract_stat.raster_dir folder not found""")

    input_geometry = os.path.join(config.extract_stat.input_geometry_dir, config.extract_stat.input_geometry_filename)

    if not os.path.isfile(input_geometry):
        raise ValueError(f"Input gemetry file not found: {input_geometry}")

    # Check output folder
    output_dir = config.extract_stat.output_dir
    if output_dir is None:
        raise ValueError(
            """config.extract_stat.output_dir is empty, please provide an output directory in the configuration"""
        )
    os.makedirs(config.extract_stat.output_dir, exist_ok=True)

    # Parameters
    spatial_ref = config.extract_stat.spatial_reference
    output_geometry = os.path.join(config.extract_stat.output_dir, config.extract_stat.output_geometry_filename)
    output_vrt = os.path.join(config.extract_stat.output_dir, config.extract_stat.output_vrt_filename)

    # Create list of input's raster and vrt
    create_list_raster_and_vrt(raster_dir, output_vrt)

    # Read the input GeoJSON
    lines_gdf = gpd.read_file(input_geometry)

    if lines_gdf.crs is None:
        lines_gdf.set_crs(epsg=spatial_ref, inplace=True)

    # Convert geometries to LineString if possible
    def to_linestring(geom):
        if geom.geom_type == "LineString":
            return geom
        elif geom.geom_type == "MultiLineString":
            return list(geom.geoms)[0]
        else:
            raise ValueError(f"Unsupported geometry type: {geom.geom_type}")

    lines_gdf["geometry"] = lines_gdf.geometry.apply(to_linestring)

    # Check lines are only LineString
    if not all(lines_gdf.geometry.geom_type.isin(["LineString"])):
        raise ValueError("Only LineString or MultiLineString geometries are supported.")

    # Keep lines inside raster (VRT created)
    lines_gdf_clip = clip_lines_by_raster(lines_gdf, output_vrt, spatial_ref)

    # Extract Z value from lines and clean the result
    lines_gdf_min_z = (
        extract_polylines_min_z_from_dsm(lines_gdf_clip, output_vrt, no_data_value=config.tile_geometry.no_data_value)
        .drop(columns=[c for c in ["index", "FID"] if c in lines_gdf.columns], errors="ignore")
        .reset_index(drop=True)
    )

    # Check lines are not empty
    if lines_gdf_min_z.empty:
        raise ValueError("All geometries returned None. Abort.")

    lines_gdf_min_z.to_file(output_geometry, driver="GeoJSON")


def main():
    logging.basicConfig(level=logging.INFO)
    run_extract_z_virtual_lines_from_raster()


if __name__ == "__main__":
    main()
