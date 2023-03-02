"""Run ground filtering for a single tile"""
import argparse
from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.las_filter import filter_las_classes
import logging
import os


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for filtering by class on a single tile " +
        "(by default keep ground + virtual points)"
    )
    parser.add_argument(
        "--input_file", "-i",
        type=str,
        required=True,
        help="Input file on which to run the pipeline " +
             "(most likely located in PDAL folder 'data'). " +
             "The script assumes that the neighbor tiles are located in the same folder as " +
             "the queried tile")
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        required=True,
        default="/tmp/ground",
        help="Directory folder for saving the filtered tile")
    # Optional parameters
    parser.add_argument(
        "--spatial_reference",
        default="EPSG:2154",
        help="Spatial reference to use to override the one from input las."
    )
    parser.add_argument(
        "--keep_classes",
        nargs='+',
        type=int,
        default=[2, 66],
        help="Classes to keep when filtering. Default: ground + virtual points"
    )
    parser.add_argument(
        "--force_output_ext",
        choices=list(commons.point_cloud_extensions),
        default=None,
        help="Force output ext to .las or .laz. If None or not set, use input extension"
    )

    return parser.parse_args()


def run_filter_on_tile(input_file, output_dir, spatial_ref="EPSG:2154", keep_classes=[2, 66],
                       output_ext=None):
    ## infer input/output paths
    # split input file
    _, input_basename = os.path.split(input_file)
    if output_ext is None:
        output_basename = input_basename
    else:
        tilename, _ = os.path.splitext(input_basename)
        output_basename = f"{tilename}.{output_ext}"

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, output_basename)

    ## process
    filter_las_classes(input_file, output_file, spatial_ref=spatial_ref, keep_classes=keep_classes)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_filter_on_tile(args.input_file,
                       args.output_dir,
                       spatial_ref=args.spatial_reference,
                       keep_classes=args.keep_classes,
                       output_ext=args.force_output_ext)


if __name__ == "__main__":
    main()
