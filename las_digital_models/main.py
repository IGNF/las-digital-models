"""Main entry point for digital models generation"""

import logging as log
import os
import tempfile
from pathlib import Path

import hydra
from omegaconf import DictConfig
from pdaltools.las_add_buffer import create_las_with_buffer
from pdaltools.las_info import get_tile_origin_using_header_info


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def main_las_digital_models(config: DictConfig):
    """Main function to generate digital models from a las file.
    It can compute:
    - DSM: digital surface model
    - DTM: digital terrain model
    - DHM: digital height model (DSM - DTM)

    If a buffer size is set in config, the las file is buffered using its neighbors
    before generating the digital models to prevent border effects.
    Neighbors search is computed based on file names:
    las files are expected to be formatted as: {prefix1}_{prefix2}_{XXXX}_{YYYY}_{suffix}
    with XXXX and YYYY their coordinates with conditions:
    - XXXX (and YYYY) * config.tile_geometry.tile_coord_scale are the coordinates of the upper left
    corner in meters
    - XXXX (and YYYY) * config.tile_geometry.tile_coord_scale + (- for YYYY) config.tile_geometry.tile_width
    are the coordinates of the lower right corner in meters

    Args:
        config (DictConfig): hydra config for the project
    """
    log.basicConfig(level=log.INFO, format="%(message)s")

    initial_las_filename = config.io.input_filename
    in_dir = config.io.input_dir
    out_dir = config.io.output_dir

    # Check input/output files and folders
    if initial_las_filename is None or in_dir is None or out_dir is None:
        raise RuntimeError(
            """In input you have to give a las, an input directory and an output directory.
            For more info run the same command by adding --help"""
        )

    os.makedirs(out_dir, exist_ok=True)

    tilename = os.path.splitext(initial_las_filename)[0]  # Noqa: F841
    initial_las_file = os.path.join(in_dir, initial_las_filename)

    with tempfile.TemporaryDirectory(prefix="tmp_buffer", dir=".") as tmpdir_buffer:
        # Get pointcloud origin from the las file metadata
        tile_origin = get_tile_origin_using_header_info(  # Noqa: F841
            initial_las_file, tile_width=config.tile_geometry.tile_width
        )

        # Buffer
        log.info(f"\nStep 1: Create buffered las file with buffer = {config.buffer.size}")
        if config.buffer.output_subdir:
            las_with_buffer = Path(out_dir) / config.buffer.output_subdir / initial_las_filename
        else:
            las_with_buffer = Path(tmpdir_buffer) / initial_las_filename
        las_with_buffer.parent.mkdir(parents=True, exist_ok=True)

        epsg = config.io.spatial_reference
        create_las_with_buffer(
            input_dir=str(in_dir),
            tile_filename=initial_las_file,
            output_filename=str(las_with_buffer),
            buffer_width=config.buffer.size,
            spatial_ref=f"EPSG:{epsg}" if str(epsg).isdigit() else epsg,
            tile_width=config.tile_geometry.tile_width,
            tile_coord_scale=config.tile_geometry.tile_coord_scale,
        )


if __name__ == "__main__":
    main_las_digital_models()
