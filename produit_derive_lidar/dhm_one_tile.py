"""Run create DHM"""
import argparse
from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.dhm_generation import calculate_dhm
import logging
import os


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for calculating DHM on a single tile"
    )
    parser.add_argument(
        "--origin_las_file", "-or",
        type=str,
        required=True,
        help="Path to the origin lidar tile (before filtering)." +
            "Used to retrieve the tile bounding box.")
    parser.add_argument(
        "--dsm_dir", "-is",
        type=str,
        required=True,
        help="Directory folder for the input DSM")
    parser.add_argument(
        "--dtm_dir", "-it",
        type=str,
        required=True,
        help="Directory folder for the input DTM")
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        required=True,
        help="Directory folder for saving the outputs")
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


def run_dhm_on_tile(input_file, input_folder_dsm, input_folder_dtm, output_dir,
                   pixel_size=1, interpolation_method='startin-Laplace'):
    ## infer input/output paths
    # split input file
    _, input_basename = os.path.split(input_file)
    tilename, _ = os.path.splitext(input_basename)

    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}_{commons.method_postfix[interpolation_method]}.tif"
    geotiff_dsm = os.path.join(input_folder_dsm, geotiff_filename)
    geotiff_dtm = os.path.join(input_folder_dtm, geotiff_filename)
    geotiff_output = os.path.join(output_dir, geotiff_filename)
    ## process
    calculate_dhm(geotiff_dsm, geotiff_dtm, geotiff_output)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    run_dhm_on_tile(args.origin_las_file, args.dsm_dir, args.dtm_dir,
                   args.output_dir, args.pixel_size, args.interpolation_method)


if __name__ == "__main__":
    main()
