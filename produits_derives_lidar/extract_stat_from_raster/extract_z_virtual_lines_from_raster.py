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

    dir_list_raster = [os.path.join(raster_dir, f) for f in os.listdir(raster_dir) if f.lower().endswith(".tif")]
    if not dir_list_raster:
        raise ValueError(f"No raster (.tif) files found in {raster_dir}")

    filename_geom, _ = os.path.splitext(config.extract_stat.input_geometry_filename)
    input_geometry = next(
        os.path.join(config.extract_stat.input_geometry_dir, f"{filename_geom}.{ext}") for ext in ("geojson", "shp")
    )  # path to the geometry file
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
    output_vrt = config.extract_stat.output_vrt_path

    # Build and save VRT file
    vrt_options = gdal.BuildVRTOptions(resampleAlg="cubic", addAlpha=True)
    my_vrt = gdal.BuildVRT(output_vrt, dir_list_raster, options=vrt_options)

    if my_vrt is None:
        raise ValueError(f"gdal.BuildVRT returned None for {output_vrt}")

    my_vrt = None

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

    # Extract Z value from lines and clean the result
    lines_gdf_min_z = (
        extract_polylines_min_z_from_dsm(lines_gdf, output_vrt, no_data_value=config.tile_geometry.no_data_value)
        .drop(columns=[c for c in ["index", "FID"] if c in lines_gdf.columns], errors="ignore")
        .reset_index(drop=True)
    )

    # Keep lines inside raster (VRT created)
    lines_gdf_min_z_final = clip_lines_by_raster(lines_gdf_min_z, output_vrt, spatial_ref)

    # Check lines are not empty
    if lines_gdf_min_z_final.empty:
        raise ValueError("All geometries returned None; output will be empty.")

    lines_gdf_min_z_final.to_file(output_geometry, driver="GeoJSON")


def main():
    logging.basicConfig(level=logging.INFO)
    run_extract_z_virtual_lines_from_raster()


if __name__ == "__main__":
    main()
