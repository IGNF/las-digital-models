""" Main script for interpolation on a single tile
Output files will be written to the target folder, tagged with the name of the interpolation
method that was used.
"""

import tempfile
import hydra
from omegaconf import DictConfig, OmegaConf
import logging
import os

from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.las_interpolation_deterministic import deterministic_method
from produit_derive_lidar.tasks.las_raster_generation import mask_with_no_data_shapefile
from pdaltools.las_info import parse_filename


log = commons.get_logger(__name__)


@commons.eval_time_with_pid
def interpolate(input_file: str,
                output_raster: str,
                config: dict):
    """Run interpolation
    Args:
        input_file(str): File on which to run the interpolation
        output_raster(str): output file for raster image (with buffer)
        config(dict): dictionary that must contain
                { "tile_geometry": { "tile_coord_scale": #int, "tile_width": #int, "pixel_size": #float, "no_data_value": #int },
                  "io": { "spatial_reference": #str},
                  "interpolation": { "algo_name": #str }
                }
            with
                tile_coord_scale value(int): coords in tile names are in km
                tile_width value(int): tile width in meters
                pixel_size value(float): pixel size for raster generation
                spatial_ref value(str): spatial reference to use when reading las file
                interpolation_method value(str): interpolation method for raster generation
    Output:
        ras: output raster (/!\ can be None for some methods)
        origin: tile origin
        can_interpolate (bool): false if there were no points to interpolate
    """
    _, coordX, coordY, _ = parse_filename(input_file)
    origin = [float(coordX) * config["tile_geometry"]["tile_coord_scale"],
              float(coordY) * config["tile_geometry"]["tile_coord_scale"]]
    nb_pixels = [int(config["tile_geometry"]["tile_width"] / config["tile_geometry"]["pixel_size"]),
                 int(config["tile_geometry"]["tile_width"] / config["tile_geometry"]["pixel_size"])]

    _interpolation = deterministic_method(nb_pixels, origin,
                                          config["tile_geometry"]["pixel_size"],
                                          config["interpolation"]["algo_name"],
                                          config["io"]["spatial_reference"],
                                          config["tile_geometry"]["no_data_value"],
                                          config["tile_geometry"]["tile_width"],
                                          config["tile_geometry"]["tile_coord_scale"])
    _interpolation.run(input_file, output_raster)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_ip_on_tile(config: DictConfig):
    """Run interpolation on single tile useing hydra config
    config parameters are explained in the default.yaml files
    """
    if config.io.input_dir is None:
        input_dir = config.io.output_dir
    else:
        input_dir = config.io.input_dir

    os.makedirs(config.io.output_dir, exist_ok=True)
    tilename, _ = os.path.splitext(config.io.input_filename)

    # input file (already filtered and potentially with a buffer)
    if config.io.forced_intermediate_ext is None:
        input_file = os.path.join(input_dir, config.io.input_filename)
    else:
        input_file = os.path.join(input_dir, f"{tilename}.{config.io.forced_intermediate_ext}")

    # for export
    _size = commons.give_name_resolution_raster(config.tile_geometry.pixel_size)
    geotiff_stem = f"{tilename}{_size}_{config.interpolation.method_postfix}"
    geotiff_filename = f"{geotiff_stem}.tif"
    geotiff_path = os.path.join(config.io.output_dir, geotiff_filename)

    ## process
    dico_config = OmegaConf.to_container(config)
    interpolate(input_file, geotiff_path, dico_config)

    if config.io.no_data_mask_shapefile:
        with tempfile.NamedTemporaryFile(suffix=".tif", prefix=f"{geotiff_stem}_raw") as tmp_geotiff:
            ## process interpolation
            interpolate(input_file, tmp_geotiff.name, config)
            mask_with_no_data_shapefile(config.io.no_data_mask_shapefile,
                                        tmp_geotiff.name,
                                        geotiff_path,
                                        config.tile_geometry.no_data_value)

    else:
        interpolate(input_file, geotiff_path, config)


def main():
    logging.basicConfig(level=logging.INFO)
    run_ip_on_tile()


if __name__ == "__main__":
    main()

