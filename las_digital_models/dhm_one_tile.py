"""Run create DHM on a single tile (current definition is DSM - DTM)"""

import logging
import os

import hydra
from omegaconf import DictConfig

from las_digital_models.commons import commons
from las_digital_models.tasks.dhm_generation import calculate_dhm

log = commons.get_logger(__name__)


def run_dhm_on_tile(
    input_las_filename: str,
    input_dtm_dir: str,
    input_dsm_dir: str,
    output_dir: str,
    pixel_size: float,
    no_data_value: float,
):
    os.makedirs(output_dir, exist_ok=True)
    tilename, _ = os.path.splitext(input_las_filename)

    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}.tif"
    geotiff_dsm = os.path.join(input_dsm_dir, geotiff_filename)
    geotiff_dtm = os.path.join(input_dtm_dir, geotiff_filename)
    geotiff_output = os.path.join(output_dir, geotiff_filename)
    # process
    calculate_dhm(geotiff_dsm, geotiff_dtm, geotiff_output, no_data_value=no_data_value)

    return


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def main(config: DictConfig):
    logging.basicConfig(level=logging.INFO)

    run_dhm_on_tile(
        input_las_filename=config.io.input_filename,
        input_dtm_dir=config.dhm.input_dtm_dir,
        input_dsm_dir=config.dhm.input_dsm_dir,
        output_dir=config.io.output_dir,
        pixel_size=config.tile_geometry.pixel_size,
        no_data_value=config.tile_geometry.no_data_value,
    )


if __name__ == "__main__":
    main()
