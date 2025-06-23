""" Main script for interpolation on a single tile
Output files will be written to the target folder, tagged with the name of the interpolation
method that was used.
"""

import logging
import os
import tempfile

import hydra
from omegaconf import DictConfig

from las_digital_models.commons import commons
from las_digital_models.tasks.las_interpolation import interpolate_from_config
from las_digital_models.tasks.postprocessing import mask_with_no_data_shapefile

log = commons.get_logger(__name__)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_ip_on_tile(config: DictConfig):
    """Run interpolation on single tile using hydra config
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
    geotiff_stem = f"{tilename}{_size}"
    geotiff_filename = f"{geotiff_stem}.tif"
    geotiff_path = os.path.join(config.io.output_dir, geotiff_filename)

    if config.io.no_data_mask_shapefile:
        with tempfile.NamedTemporaryFile(suffix=".tif", prefix=f"{geotiff_stem}_raw") as tmp_geotiff:
            # process interpolation
            interpolate_from_config(input_file, tmp_geotiff.name, config)
            mask_with_no_data_shapefile(
                config.io.no_data_mask_shapefile, tmp_geotiff.name, geotiff_path, config.tile_geometry.no_data_value
            )

    else:
        interpolate_from_config(input_file, geotiff_path, config)


def main():
    logging.basicConfig(level=logging.INFO)
    run_ip_on_tile()


if __name__ == "__main__":
    main()
