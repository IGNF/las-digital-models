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

from las_digital_models.commons import commons
from las_digital_models.extract_stat_from_raster.rasters.extract_z_min_from_raster_by_polylines import (
    clip_lines_by_raster,
    extract_polylines_min_z_from_dsm,
)
from las_digital_models.extract_stat_from_raster.vectors.clip_geometry import (
    clip_lines_by_polygons,
)

gdal.UseExceptions()

log = commons.get_logger(__name__)


def create_vrt(dir_list_raster: list, output_vrt: str):
    """Create vrt from raster files in a directory.

    Args:
        dir_list_raster (List): ist of input raster files.
        output_vrt (str): Path to the output VRT file.

    Raises:
        ValueError: If the VRT doesn't create
    """
    # Build and save VRT file
    vrt_options = gdal.BuildVRTOptions(resampleAlg="cubic", addAlpha=True)
    my_vrt = gdal.BuildVRT(output_vrt, dir_list_raster, options=vrt_options)

    if my_vrt is None:
        raise ValueError(f"gdal.BuildVRT returned None for {output_vrt}")

    my_vrt = None  # necessary to close the VRT file properly


@hydra.main(config_path="../../configs/", config_name="config.yaml", version_base="1.2")
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
        raise ValueError(
            f"""config.extract_stat.input_raster_dir ({config.extract_stat.input_raster_dir}) not found"""
        )

    input_geometry = os.path.join(config.extract_stat.input_geometry_dir, config.extract_stat.input_geometry_filename)

    if not os.path.isfile(input_geometry):
        raise ValueError(f"Input geometry file not found: {input_geometry}")

    dir_list_raster = [os.path.join(raster_dir, f) for f in os.listdir(raster_dir) if f.lower().endswith(".tif")]
    if not dir_list_raster:
        raise ValueError(f"No raster (.tif) files found in {raster_dir}")

    input_clip_geometry = os.path.join(
        config.extract_stat.input_clip_geometry_dir, config.extract_stat.input_clip_geometry_filename
    )
    # path to the geometry file
    if not os.path.isfile(input_geometry):
        raise ValueError(f"Input geometry file not found: {input_clip_geometry}")

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

    # Create  vrt
    create_vrt(dir_list_raster, output_vrt)

    # Read the input GeoJSON
    geom_gdf = gpd.read_file(input_geometry)
    polygons_gdf = gpd.read_file(input_clip_geometry)

    # Convert geometries to LineString (no more MultiLineString)
    mask = geom_gdf.geometry.geom_type.isin(['LineString', 'MultiLineString'])
    lines_gdf = geom_gdf.loc[mask].explode(index_parts=False).reset_index(drop=True)

    if geom_gdf.crs is None:
        geom_gdf.set_crs(epsg=spatial_ref, inplace=True)

    if polygons_gdf.crs is None:
        polygons_gdf.set_crs(epsg=spatial_ref, inplace=True)

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

    # Clip lines by bridges
    geoms_gdf_min_z_clip = clip_lines_by_polygons(lines_gdf_min_z, polygons_gdf)
    
    # Convert geometries to LineString (no more MultiLineString)
    mask = geoms_gdf_min_z_clip.geometry.geom_type.isin(['LineString', 'MultiLineString'])
    lines_gdf_min_z_clip = geoms_gdf_min_z_clip.loc[mask].explode(index_parts=False).reset_index(drop=True)

    lines_gdf_min_z_clip.to_file(output_geometry, driver="GeoJSON")


def main():
    logging.basicConfig(level=logging.INFO)
    run_extract_z_virtual_lines_from_raster()


if __name__ == "__main__":
    main()
