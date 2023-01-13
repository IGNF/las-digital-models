"""Run ground filtering for a single tile"""
import argparse
from lidar_prod.commons import commons
from lidar_prod.tasks.las_filter import filter_las_classes
import logging
import os


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for filtering by class on a single tile " +
        "(by default keep ground + virtual points)",
        epilog="""All IDW parameters are optional, but it is assumed the user will fine-tune them,
        hence the defaults are not listed.
        Output files will be written to the target folder, tagged with thename of the interpolation
        method that was used."""
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
        help="Directory folder for saving the outputs")
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

    return parser.parse_args()


def run_gf_on_tile(input_file, output_dir, spatial_ref="EPSG:2154", keep_classes=[2, 66]):
    ## infer input/output paths
    # split input file
    _, input_basename = os.path.split(input_file)
    tilename, _ = os.path.splitext(input_basename) # here, extension is like ".las"

    # for ground extraction
    ground_file = os.path.join(output_dir, f"{tilename}_ground.las")

    ## process
    filter_las_classes(input_file, ground_file, spatial_ref=spatial_ref, keep_classes=keep_classes)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_gf_on_tile(args.input_file, args.output_dir, spatial_ref=args.spatial_reference,
                   keep_classes=args.keep_classes)


if __name__ == "__main__":
    main()
