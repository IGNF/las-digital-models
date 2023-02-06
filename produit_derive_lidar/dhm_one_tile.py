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
        "--origin_file", "-i",
        type=str,
        required=True,
        help="Path to the origin lidar tile (before filtering)." +
            "Used to retrieve the tile bounding box.")
    parser.add_argument(
        "--origin_file_dsm", "-i_s",
        type=str,
        required=True,
        help="Directory folder for creating DSM")
    parser.add_argument(
        "--origin_file_dtm", "-i_t",
        type=str,
        required=True,
        help="Directory folder for creating DTM")
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
        "--postprocessing", "-p",
        type=int,
        default=0,
        choices=range(5),
        help="""
        post-processing mode, currently these ones are available:
          - 0 (default, does not run post-processing)
          - 1 (runs missing pixel value patching only)
          """)
    parser.add_argument(
        "--pixel_size", "-s",
        type=float,
        default=1,
        help="pixel size (in metres) for interpolation")
    parser.add_argument(
        "--interpolation_method", "-m",
        type=str,
        default="startin-Laplace",
        choices=["startin-TINlinear", "startin-Laplace",
                 "CGAL-NN", "PDAL-IDW", "IDWquad"],
        help="interpolation method)")
    # Optional parameters
    parser.add_argument(
        "--spatial_reference",
        default="EPSG:2154",
        help="Spatial reference to use to override the one from input las."
    )

    return parser.parse_args()


def run_dhm_on_tile(input_file, input_file_mns, input_file_mnt, temp_dir, output_dir,
                   pixel_size=1, interpolation_method='startin-Laplace',
                postprocessing_mode=0, spatial_ref="EPSG:2154"):
    ## infer input/output paths
    # split input file
    input_dir, input_basename = os.path.split(input_file)
    tilename, extension = os.path.splitext(input_basename) # here, extension is like ".LAS"

    # for export
    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}_{commons.method_postfix[interpolation_method]}.tif"
    geotiff_dsm = os.path.join(output_dir.replace("DHM", "DSM"), geotiff_filename)
    geotiff_dtm = os.path.join(output_dir.replace("DHM", "DTM"), geotiff_filename)
    geotiff_output = os.path.join(output_dir, geotiff_filename)
    ## process
    calculate_dhm(geotiff_dsm, geotiff_dtm, geotiff_output)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    run_dhm_on_tile(args.origin_file, args.origin_file_mns, args.origin_file_mnt,
                   args.temp_dir, args.output_dir,
                   args.pixel_size, args.interpolation_method, args.postprocessing)


if __name__ == "__main__":
    main()
