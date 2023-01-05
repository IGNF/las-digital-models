"""Run ground filtering for a single tile"""
import argparse
from lidar_prod.commons import commons
from lidar_prod.tasks.las_ground import filter_las_ground
import os


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for ground filtering on a single tile",
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

    return parser.parse_args()


def run_gf_on_tile(input_file, output_dir, spatial_ref="EPSG:2154"):
    ## infer input/output paths
    # split input file
    _, input_basename = os.path.split(input_file)
    tilename, _ = os.path.splitext(input_basename) # here, extension is like ".las"

    # for ground extraction
    ground_file = os.path.join(output_dir, f"{tilename}_ground.las")

    ## process
    filter_las_ground(input_file, ground_file, spatial_ref=spatial_ref)

    return


if __name__ == "__main__":
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_gf_on_tile(args.input_file, args.output_dir, spatial_ref=args.spatial_reference)