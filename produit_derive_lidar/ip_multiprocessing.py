# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR INTERPOLATION + POST-PROCESSING
#             PRIMARY ENTRY POINT FOR PROGRAM

import argparse
from produit_derive_lidar.commons import commons
from produit_derive_lidar.ip_one_tile import run_ip_on_tile
import logging
from multiprocessing import Pool
import os


def parse_args():
    parser = argparse.ArgumentParser("Main script for interpolation",
        epilog="""Output files will be written to the target folder, tagged with the name of the
        interpolation method that was used.""")
    parser.add_argument(
        "--origin_dir", "-or",
        type=str,
        required=True,
        help="Folder containing the origin lidar tiles (before filtering)." +
            "Used to retrieve the tile bounding box.")
    parser.add_argument(
        "--input_las_dir", "-i",
        type=str,
        default="/tmp/ground",
        help="Folder containing the input tiles (filtered and potentially with buffer added).")
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        required=True,
        help="Directory folder for saving the outputs.")
    parser.add_argument(
        "--temp_dir", "-t",
        type=str,
        default = "/tmp",
        help="Directory folder for saving intermediate results")
    parser.add_argument(
        "--extension", "-e",
        type=str.lower,
        default="las",
        choices=["las", "laz"],
        help="extension of the origin tile file")
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
    parser.add_argument(
        "--cpu_limit",
        type=int,
        default=-1,
        help="Maximum number of cpus to use (Default: use cpu_count - 1)"
    )

    return  parser.parse_args()


def ip_worker(args):
    """Function to pass arguments to run_ip_on_tile as a list (for multiprocessing)
    """
    run_ip_on_tile(*args)


def start_pool(origin_dir: str,
               input_las_dir: str,
               output_dir: str,
               temp_dir: str='/tmp',
               filetype: str='las',
               size: int=1,
               method: str='startin-Laplace',
               spatial_ref: str="EPSG:2154",
               cpu_limit: int=-1):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(origin_dir, filetype)
    num_threads = commons.select_num_threads(display_name="interpolation", cpu_limit=cpu_limit)

    if len(fnames) == 0:
        raise ValueError("No file names were input")

    pre_map = [[os.path.join(origin_dir, fn), input_las_dir, temp_dir, output_dir, size, method,
                spatial_ref]
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
    start_pool(args.origin_dir, args.input_las_dir, args.output_dir, args.temp_dir,
               filetype=args.extension,
               size=args.pixel_size,
               method=args.interpolation_method,
               spatial_ref=args.spatial_reference,
               cpu_limit=args.cpu_limit)


if __name__ == '__main__':
    main()