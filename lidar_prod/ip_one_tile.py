"""Run interpolation + postprocessing for a single tile on ground filtered tiles"""
import argparse
from lidar_prod.commons import commons
from lidar_prod.tasks.las_prepare import las_prepare
from lidar_prod.tasks.las_interpolation_deterministic import deterministic_method
from lidar_prod.tasks.las_raster_generation import export_raster
import os


log = commons.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        "Main script for preprocessing +interpolation + post-processing on a single tile",
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
             "(with ground already filtered). " +
             "The script assumes that the neighbor tiles are located in the same folder as " +
             "the queried tile")
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
          - 2 (runs basic flattening only)
          - 3 (runs both patching and basic flattening)
          - 4 (runs patching, basic flattening and hydro-flattening)
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


@commons.eval_time_with_pid
def interpolate(input_dir, input_file, merge_file, output_file, output_raster,
        pixel_size, interpolation_method, spatial_ref="EPSG:2154"):
    gnd_coords, res, origin = las_prepare(input_dir, input_file, merge_file, output_file,
        pixel_size, spatial_ref=spatial_ref)
    _interpolation = deterministic_method(gnd_coords, res, origin, pixel_size, interpolation_method,
                                          spatial_ref=spatial_ref)
    ras = _interpolation.run(pdal_idw_input=output_file, pdal_idw_output=output_raster)

    return ras, origin


def run_ip_on_tile(input_file, temp_dir, output_dir,
        pixel_size=1, interpolation_method='startin-Laplace',
        postprocessing_mode=0, spatial_ref="EPSG:2154"):
    ## infer input/output paths
    # split input file
    input_dir, input_basename = os.path.split(input_file)
    tilename, extension = os.path.splitext(input_basename) # here, extension is like ".las"

    # for buffer addition
    merge_file = os.path.join(temp_dir, f"{tilename}_merge.las")
    buffer_file = os.path.join(temp_dir, f"{tilename}_crop.las")

    # for ground extraction
    ground_dir =output_dir
    ground_file = os.path.join(ground_dir, f"{tilename}_ground.las")

    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}_{commons.method_postfix[interpolation_method]}.tif"
    geotiff_path_temp = os.path.join(temp_dir, geotiff_filename)
    geotiff_path = os.path.join(output_dir, geotiff_filename)

    ## process
    ras, origin = interpolate(ground_dir, ground_file, merge_file, buffer_file, geotiff_path_temp,
            pixel_size, interpolation_method, spatial_ref=spatial_ref)

    export_raster(input_file, ras, origin, pixel_size, geotiff_path_temp,
        geotiff_path, interpolation_method, spatial_ref)

    return


if __name__ == "__main__":
    args = parse_args()

    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    run_ip_on_tile(args.input_file, args.temp_dir, args.output_dir,
        args.pixel_size, args.interpolation_method, args.postprocessing,
        spatial_ref=args.spatial_reference)