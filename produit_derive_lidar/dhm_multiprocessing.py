"""Run create DHM"""
import argparse
from produit_derive_lidar.commons import commons
from produit_derive_lidar.dhm_one_tile import run_dhm_on_tile
import logging
from multiprocessing import Pool
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


def ip_worker(args):
    """Function to pass arguments to run_ip_on_tile as a list (for multiprocessing)
    """
    run_dhm_on_tile(*args)


def start_pool(origin_dir: str,
               filtered_las_dir: str,
               output_dir: str,
               temp_dir: str='/tmp',
               filetype: str='las',
               postprocess: int=0,
               size: int=1,
               method: str='startin-Laplace',
               spatial_ref: str="EPSG:2154",
               buffer_width: int=100,
               cpu_limit: int=-1):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(origin_dir, filetype)
    num_threads = commons.select_num_threads(display_name="interpolation", cpu_limit=cpu_limit)

    if len(fnames) == 0:
        raise ValueError("No file names were input")

    pre_map = [[os.path.join(origin_dir, fn), filtered_las_dir, temp_dir, output_dir, size, method,
                postprocess, spatial_ref, buffer_width]
               for fn in fnames]
    with Pool(num_threads) as p:
        p.map(ip_worker, pre_map)
        # Pool close and join are still required when using a context manager
        # cf. https://superfastpython.com/multiprocessing-pool-context-manager/
        p.close()
        p.join()


    logging.info("All workers have returned.")


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    # Create the severals folder if not exists
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.temp_dir, exist_ok=True)
    start_pool(args.origin_file, args.origin_file_dsm, args.origin_file_dtm,
               args.temp_dir, args.output_dir,
               args.pixel_size, args.interpolation_method, args.postprocessing,
               cpu_limit=args.cpu_limit)


if __name__ == '__main__':
    main()
