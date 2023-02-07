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
        "--origin_las_dir", "-or",
        type=str,
        required=True,
        help="Path to the origin lidar tile (before filtering)." +
            "Used to retrieve the tile name.")
    parser.add_argument(
        "--extension", "-e",
        type=str.lower,
        default="las",
        choices=["las", "laz"],
        help="extension of the origin lidar files")
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
    parser.add_argument(
        "--cpu_limit",
        type=int,
        default=-1,
        help="Maximum number of cpus to use (Default: use cpu_count - 1)"
    )

    return parser.parse_args()


def ip_worker(args):
    """Function to pass arguments to run_ip_on_tile as a list (for multiprocessing)
    """
    run_dhm_on_tile(*args)


def start_pool(origin_las_dir: str,
               dsm_dir: str,
               dtm_dir: str,
               output_dir: str,
               pixel_size: int,
               interpolation_method: str,
               cpu_limit: int=-1,
               filetype: str='las'):

    """Assembles and executes the multiprocessing pool.
    """
    fnames = commons.listPointclouds(origin_las_dir, filetype)
    num_threads = commons.select_num_threads(display_name="interpolation", cpu_limit=cpu_limit)

    if len(fnames) == 0:
        raise ValueError("No file names were input")

    pre_map = [[os.path.join(origin_las_dir, fn), dsm_dir, dtm_dir, output_dir, pixel_size,
        interpolation_method]
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
    start_pool(args.origin_las_dir,
               args.dsm_dir,
               args.dtm_dir,
               args.output_dir,
               args.pixel_size,
               args.interpolation_method,
               cpu_limit=args.cpu_limit,
               filetype=args.extension)


if __name__ == '__main__':
    main()
