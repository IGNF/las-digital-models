"""Run interpolation + postprocessing for a single tile on ground filtered tiles"""
import argparse
from lidar_prod.commons import commons
from lidar_prod.commons.laspy_io import read_las_file_to_numpy
from lidar_prod.tasks.las_interpolation_deterministic import deterministic_method
from lidar_prod.tasks.las_raster_generation import export_and_clip_raster
from las_stitching.las_add_buffer import create_las_with_buffer
import logging
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
        "--ground_dir", "-g",
        type=str,
        required=False,  # set to None if not provided
        help="Folder containing the ground results (set to `--output_dir` if not provided).")
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
    parser.add_argument(
        "--buffer_width",
        default=100,
        type=int,
        help="Width (in meter) for the buffer that is added to the tile before interpolation " +
             "(to prevent artefacts)"
    )

    return parser.parse_args()


@commons.eval_time_with_pid
def add_buffer_and_interpolate(input_dir: str,
                input_file: str,
                buffer_file: str,
                output_raster: str,
                pixel_size: int=1,
                interpolation_method: str="startin-Laplace",
                spatial_ref: str="EPSG:2154",
                buffer_width: str=100):
    """Run interpolation with data preparation (adding a buffer around the las tile)
    Args:
        input_dir(str): Directory to look for neighbors in (for buffer addition)
        input_file(str): File on which to run the buffer addition + interpolation
        buffer_file(str): output las file with buffer
        output_raster(str): output file for raster image (with buffer)
        pixel_size(int): pixel size for raster generation
        interpolation_method(str): interpolation method for raster generation
        spatial_ref(str): spatial reference to use when reading las file
        buffer_width(int): size of the buffer to add (in meters)

    interpolate(ground_dir, ground_file, merge_file, buffer_file, geotiff_path_temp,
            pixel_size, interpolation_method, spatial_ref=spatial_ref, buffer_width=buffer_width)

    """
    create_las_with_buffer(input_dir, input_file, buffer_file,
                           buffer_width=buffer_width,
                           spatial_ref=spatial_ref)

    gnd_coords, res, origin = read_las_file_to_numpy(buffer_file, pixel_size)

    _interpolation = deterministic_method(gnd_coords, res, origin, pixel_size, interpolation_method,
                                          spatial_ref=spatial_ref)

    ras = _interpolation.run(pdal_idw_input=buffer_file, pdal_idw_output=output_raster)

    return ras, origin


def run_ip_on_tile(input_file, ground_dir, temp_dir, output_dir,
        pixel_size=1, interpolation_method='startin-Laplace',
        postprocessing_mode=0, spatial_ref="EPSG:2154", buffer_width=100):
    ## infer input/output paths
    # split input file
    input_dir, input_basename = os.path.split(input_file)
    tilename, extension = os.path.splitext(input_basename) # here, extension is like ".las"

    # for buffer addition
    buffer_dir = os.path.join(temp_dir, "crop")
    os.makedirs(buffer_dir, exist_ok=True)
    buffer_file = os.path.join(buffer_dir, f"{tilename}.las")

    # for ground extraction
    ground_file = os.path.join(ground_dir, f"{tilename}.las")

    # for export
    _size = commons.give_name_resolution_raster(pixel_size)
    geotiff_filename = f"{tilename}{_size}_{commons.method_postfix[interpolation_method]}.tif"
    geotiff_path_temp = os.path.join(temp_dir, geotiff_filename)
    geotiff_path = os.path.join(output_dir, geotiff_filename)

    ## process
    ras, origin = add_buffer_and_interpolate(ground_dir, ground_file, buffer_file,
            geotiff_path_temp, pixel_size, interpolation_method, spatial_ref=spatial_ref,
            buffer_width=buffer_width)

    export_and_clip_raster(input_file, ras, origin, pixel_size, geotiff_path_temp,
        geotiff_path, interpolation_method, spatial_ref)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    ground_dir = args.output_dir if args.ground_dir is None else args.ground_dir

    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    run_ip_on_tile(args.input_file, ground_dir, args.temp_dir, args.output_dir,
        args.pixel_size, args.interpolation_method, args.postprocessing,
        spatial_ref=args.spatial_reference,
        buffer_width=args.buffer_width)


if __name__ == "__main__":
    main()
