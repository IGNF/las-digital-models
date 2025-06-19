"""Run create DHM on a single tile (current definition is DSM - DTM)"""

import logging
import os

import hydra
from omegaconf import DictConfig

from las_digital_models.commons import commons
from las_digital_models.tasks.dhm_generation import calculate_dhm

log = commons.get_logger(__name__)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_dhm_on_tile(config: DictConfig):
    os.makedirs(config.io.output_dir, exist_ok=True)
    tilename, _ = os.path.splitext(config.io.input_filename)

    # for export
    _size = commons.give_name_resolution_raster(config.tile_geometry.pixel_size)
    geotiff_filename = f"{tilename}{_size}.tif"
    geotiff_dsm = os.path.join(config.dhm.input_dsm_dir, geotiff_filename)
    geotiff_dtm = os.path.join(config.dhm.input_dtm_dir, geotiff_filename)
    geotiff_output = os.path.join(config.io.output_dir, geotiff_filename)
    # process
    calculate_dhm(geotiff_dsm, geotiff_dtm, geotiff_output, no_data_value=config.tile_geometry.no_data_value)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    run_dhm_on_tile()


if __name__ == "__main__":
    main()
