"""Main script for interpolation on a single tile
Output files will be written to the target folder, tagged with the name of the interpolation
method that was used.
"""

import logging
import os
import tempfile
from typing import List, Tuple

import hydra
from omegaconf import DictConfig
from pdaltools.las_info import parse_filename

from las_digital_models.commons import commons
from las_digital_models.tasks.las_interpolation import interpolate
from las_digital_models.tasks.postprocessing import mask_with_no_data_shapefile

log = commons.get_logger(__name__)


def run_ip_on_tile(
    input_dir: str,
    input_filename: str,
    output_dir: str,
    origin: Tuple[int, int],
    pixel_size: float,
    tile_width: int,
    spatial_reference: str,
    no_data_value: float,
    no_data_mask_shapefile: str,
    filter_dimension: str,
    filter_keep_values: List[int],
):
    """Run interpolation on single tile with geometry masking in case a mask is provided"""

    # Generate output filenames
    tilename, _ = os.path.splitext(input_filename)
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_stem = f"{tilename}{_size}"
    geotiff_filename = f"{geotiff_stem}.tif"
    geotiff_path = os.path.join(output_dir, geotiff_filename)

    input_path = os.path.join(input_dir, input_filename)
    os.makedirs(output_dir, exist_ok=True)

    if no_data_mask_shapefile:
        with tempfile.NamedTemporaryFile(suffix=".tif", prefix=f"{geotiff_stem}_raw") as tmp_geotiff:
            # process interpolation
            interpolate(
                input_path,
                tmp_geotiff.name,
                origin,
                pixel_size,
                tile_width,
                spatial_reference,
                no_data_value,
                filter_dimension,
                filter_keep_values,
            )
            mask_with_no_data_shapefile(no_data_mask_shapefile, tmp_geotiff.name, geotiff_path, no_data_value)

    else:
        interpolate(
            input_path,
            geotiff_path,
            origin,
            pixel_size,
            tile_width,
            spatial_reference,
            no_data_value,
            filter_dimension,
            filter_keep_values,
        )


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def main(config: DictConfig):
    logging.basicConfig(level=logging.INFO)

    # Use filename to get the tile coordinates.
    # Coordinates are needed to define neighboring tiles, in order to create the buffered tile.
    input_path = os.path.join(config.io.input_dir, config.io.input_filename)
    _, coordX, coordY, _ = parse_filename(input_path)
    origin = [
        float(coordX) * config.tile_geometry.tile_coord_scale,
        float(coordY) * config.tile_geometry.tile_coord_scale,
    ]

    run_ip_on_tile(
        input_dir=config.io.input_dir,
        input_filename=config.io.input_filename,
        origin=origin,
        output_dir=config.io.output_dir,
        pixel_size=config.tile_geometry.pixel_size,
        tile_width=config.tile_geometry.tile_width,
        spatial_reference=config.io.spatial_reference,
        no_data_value=config.tile_geometry.no_data_value,
        no_data_mask_shapefile=config.io.no_data_mask_shapefile,
        filter_dimension=config.interpolation.custom.filter.dimension,
        filter_keep_values=config.interpolation.custom.filter.keep_values,
    )


if __name__ == "__main__":
    main()
