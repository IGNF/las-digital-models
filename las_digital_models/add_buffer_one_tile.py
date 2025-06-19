"""Add a buffer around the queried tile from its neighbors
The script assumes that the neighbor tiles are located in the same folder as
the queried tile

"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pdaltools.las_add_buffer import create_las_with_buffer

from las_digital_models.commons import commons

log = commons.get_logger(__name__)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_add_buffer_one_tile(config: DictConfig):
    """
    The script assumes that the neighbor tiles are located in the same folder as
    the queried tile
    """

    if config.io.forced_intermediate_ext is None:
        input_file = os.path.join(config.io.input_dir, config.io.input_filename)
        output_file = os.path.join(config.io.output_dir, config.io.input_filename)
    else:
        _, input_basename = os.path.split(config.io.input_filename)
        tilename, _ = os.path.splitext(input_basename)
        input_file = os.path.join(config.io.input_dir, f"{tilename}.{config.io.forced_intermediate_ext}")
        output_file = os.path.join(config.io.output_dir, f"{tilename}.{config.io.forced_intermediate_ext}")

    os.makedirs(config.io.output_dir, exist_ok=True)

    create_las_with_buffer(
        input_dir=config.io.input_dir,
        tile_filename=input_file,
        output_filename=output_file,
        buffer_width=config.buffer.size,
        spatial_ref=config.io.spatial_reference,
        tile_width=config.tile_geometry.tile_width,
        tile_coord_scale=config.tile_geometry.tile_coord_scale,
    )


def main():
    logging.basicConfig(level=logging.INFO)
    run_add_buffer_one_tile()


if __name__ == "__main__":
    main()
