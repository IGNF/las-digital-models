"""Main entry point for digital models generation"""

import logging as log
import os
import tempfile
from pathlib import Path

import hydra
from omegaconf import DictConfig
from pdaltools.las_add_buffer import create_las_with_buffer
from pdaltools.las_info import get_tile_origin_using_header_info

from las_digital_models.dhm_one_tile import run_dhm_on_tile
from las_digital_models.ip_one_tile import run_ip_on_tile


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
    in_dir = Path(config.io.input_dir)
    out_dir = Path(config.io.output_dir)

    # Check input/output files and folders
    if initial_las_filename is None or in_dir is None or out_dir is None:
        raise RuntimeError(
            """In input you have to give a las, an input directory and an output directory.
            For more info run the same command by adding --help"""
        )

    os.makedirs(out_dir, exist_ok=True)

    with (
        tempfile.TemporaryDirectory(prefix="tmp_buffer", dir=".") as tmpdir_buffer,
        tempfile.TemporaryDirectory(prefix="tmp_dtm", dir=".") as tmpdir_dtm,
        tempfile.TemporaryDirectory(prefix="tmp_dsm", dir=".") as tmpdir_dsm,
    ):
        # Get pointcloud origin from the las file metadata
        tile_origin = get_tile_origin_using_header_info(
            in_dir / initial_las_filename, tile_width=config.tile_geometry.tile_width
        )
        # Buffer
        if config.buffer.size:
            log.info(f"Create buffered las file with buffer = {config.buffer.size}")
            if config.buffer.output_subdir:
                buffer_output_dir = Path(out_dir) / config.buffer.output_subdir
            else:
                buffer_output_dir = Path(tmpdir_buffer)
            buffer_output_dir.mkdir(parents=True, exist_ok=True)

            epsg = config.io.spatial_reference
            create_las_with_buffer(
                input_dir=str(in_dir),
                tile_filename=str(in_dir / initial_las_filename),
                output_filename=str(buffer_output_dir / initial_las_filename),
                buffer_width=config.buffer.size,
                spatial_ref=f"EPSG:{epsg}" if str(epsg).isdigit() else epsg,
                tile_width=config.tile_geometry.tile_width,
                tile_coord_scale=config.tile_geometry.tile_coord_scale,
            )
        else:
            log.info("Skip las buffer creation")
            buffer_output_dir = in_dir

        # Compute DTM
        if config.tasks.dtm or config.tasks.dhm:
            log.info("Create DTM")
            dtm_output_dir = (
                os.path.join(out_dir, config.interpolation.dtm.output_subfolder) if config.tasks.dtm else tmpdir_dtm
            )
            run_ip_on_tile(
                input_dir=buffer_output_dir,
                input_filename=initial_las_filename,
                origin=tile_origin,
                output_dir=dtm_output_dir,
                pixel_size=config.tile_geometry.pixel_size,
                tile_width=config.tile_geometry.tile_width,
                spatial_reference=config.io.spatial_reference,
                no_data_value=config.tile_geometry.no_data_value,
                no_data_mask_shapefile=config.io.no_data_mask_shapefile,
                filter_dimension=config.interpolation.dtm.filter.dimension,
                filter_keep_values=config.interpolation.dtm.filter.keep_values,
            )

        # Compute DSM
        if config.tasks.dsm or config.tasks.dhm:
            log.info("Create DSM")
            dsm_output_dir = (
                os.path.join(out_dir, config.interpolation.dsm.output_subfolder) if config.tasks.dsm else tmpdir_dsm
            )
            run_ip_on_tile(
                input_dir=buffer_output_dir,
                input_filename=initial_las_filename,
                origin=tile_origin,
                output_dir=dsm_output_dir,
                pixel_size=config.tile_geometry.pixel_size,
                tile_width=config.tile_geometry.tile_width,
                spatial_reference=config.io.spatial_reference,
                no_data_value=config.tile_geometry.no_data_value,
                no_data_mask_shapefile=config.io.no_data_mask_shapefile,
                filter_dimension=config.interpolation.dsm.filter.dimension,
                filter_keep_values=config.interpolation.dsm.filter.keep_values,
            )

        # Compute DHM
        if config.tasks.dhm:
            log.info("Create DHM")
            dhm_output_dir = os.path.join(out_dir, config.dhm.output_subfolder)
            run_dhm_on_tile(
                input_las_filename=initial_las_filename,
                input_dtm_dir=dtm_output_dir,
                input_dsm_dir=dsm_output_dir,
                output_dir=dhm_output_dir,
                pixel_size=config.tile_geometry.pixel_size,
                no_data_value=config.tile_geometry.no_data_value,
            )


if __name__ == "__main__":
    main_las_digital_models()
