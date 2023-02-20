"""Run interpolation for a single tile on filtered (and buffered) tiles"""
import argparse
from produit_derive_lidar.commons import commons
from produit_derive_lidar.commons.laspy_io import read_las_file_to_numpy
from produit_derive_lidar.tasks.las_interpolation_deterministic import deterministic_method
from produit_derive_lidar.tasks.las_raster_generation import export_and_clip_raster
import logging
import os
import numpy as np


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for interpolation on a single tile",
        epilog="""Output files will be written to the target folder, tagged with the name of the
        interpolation method that was used."""
    )
    parser.add_argument(
        "--origin_file", "-or",
        type=str,
        required=True,
        help="Path to the origin lidar tile (before filtering)." +
            "Used to retrieve the tile bounding box.")
    parser.add_argument(
        "--input_las_dir", "-i",
        type=str,
        required=False,  # set to None if not provided
        help="Folder containing the input tiles (filtered and potentially with buffer added)." +
             "(set to `--output_dir` if not provided).")
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        required=True,
        help="Directory folder for saving the outputs")
    parser.add_argument(
        "--temp_dir", "-t",
        type=str,
        default="/tmp",
        help="Temporary folder for intermediate results")
    parser.add_argument(
        "--pixel_size", "-s",
        type=float,
        default=1,
        help="pixel size (in metres) for interpolation")
    parser.add_argument(
        "--interpolation_method", "-m",
        type=str,
        default="startin-Laplace",
        choices=list(commons.method_postfix.keys()),
        help="interpolation method)")
    # Optional parameters
    parser.add_argument(
        "--spatial_reference",
        default="EPSG:2154",
        help="Spatial reference to use to override the one from input las."
    )

    return parser.parse_args()


@commons.eval_time_with_pid
def interpolate(input_file: str,
                output_raster: str,
                pixel_size: int=1,
                interpolation_method: str="startin-Laplace",
                spatial_ref: str="EPSG:2154"):
    """Run interpolation
    Args:
        input_file(str): File on which to run the interpolation
        output_raster(str): output file for raster image (with buffer)
        pixel_size(int): pixel size for raster generation
        interpolation_method(str): interpolation method for raster generation
        spatial_ref(str): spatial reference to use when reading las file
    """
    points_np, res, origin = read_las_file_to_numpy(input_file, pixel_size)

    if points_np.size > 0:
        _interpolation = deterministic_method(points_np, res, origin, pixel_size, interpolation_method,
                                            spatial_ref=spatial_ref)
        ras = _interpolation.run(pdal_input=input_file, pdal_output=output_raster)

    else:
        ras = None

    return ras, origin


def run_ip_on_tile(origin_file,
                   input_dir,
                   temp_dir,
                   output_dir,
                   pixel_size=1,
                   interpolation_method='startin-Laplace',
                   spatial_ref="EPSG:2154"):
    ## infer input/output paths
    # split origin file (used for bounds retrieval)
    origin_dir, origin_basename = os.path.split(origin_file)
    tilename, extension = os.path.splitext(origin_basename) # here, extension is like ".las"

    # input file (already filtered and potentially with a buffer)
    input_file = os.path.join(input_dir, f"{tilename}.las")

    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}_{commons.method_postfix[interpolation_method]}.tif"
    geotiff_path_temp = os.path.join(temp_dir, geotiff_filename)
    geotiff_path = os.path.join(output_dir, geotiff_filename)

    ## process
    ras, origin, = interpolate(input_file,
                              geotiff_path_temp,
                              pixel_size,
                              interpolation_method,
                              spatial_ref=spatial_ref)

    force_save_ras = False
    if ras is None:
        _, res, origin = read_las_file_to_numpy(origin_file, pixel_size)
        ras = commons.no_data_value * np.ones([res[1], res[0]])
        force_save_ras = True

    export_and_clip_raster(origin_file, ras, origin, pixel_size, geotiff_path_temp,
    geotiff_path, interpolation_method, spatial_ref, force_save_ras=force_save_ras)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    input_las_dir = args.output_dir if args.input_las_dir is None else args.input_las_dir

    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    run_ip_on_tile(args.origin_file, input_las_dir, args.temp_dir, args.output_dir,
        args.pixel_size, args.interpolation_method,
        spatial_ref=args.spatial_reference)


if __name__ == "__main__":
    main()
