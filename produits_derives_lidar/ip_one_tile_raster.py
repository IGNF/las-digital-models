""" Main script for extract z virtual lines on a single tile (raster)
Output files will be written to the target folder, tagged with the name of the tile that was used.
"""

import logging
import os

import hydra
from omegaconf import DictConfig

from produits_derives_lidar.commons import commons
from produits_derives_lidar.extract_stat_from_raster.extract_z_virtual_lines_from_raster import (
    extract_z_virtual_lines_from_raster,
)

log = commons.get_logger(__name__)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_ip_on_tile_raster(config: DictConfig):
    """Run extract z virtual lines on single tile using hydra config
    config parameters are explained in the default.yaml files
    """
    os.makedirs(config.io.output_dir, exist_ok=True)
    tilename_raster, _ = os.path.splitext(config.io.input_raster_filename)
    input_raster = os.path.join(config.io.input_raster_dir, f"{tilename_raster}.tif")  # path to the RASTER file

    tilename_geom, _ = os.path.splitext(config.io.input_geometry_filename)
    input_geometry = os.path.join(config.io.input_geometry_dir, f"{tilename_geom}.shp")  # path to the geometry file

    # for export
    crs = config.io.spatial_reference
    geometry_filename = f"{tilename_raster}_lines.GeoJSON"
    output_geometry = os.path.join(config.io.output_dir, geometry_filename)

    extract_z_virtual_lines_from_raster(input_geometry, input_raster, output_geometry, crs)


def main():
    logging.basicConfig(level=logging.INFO)
    run_ip_on_tile_raster()


if __name__ == "__main__":
    main()
