# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR PRE-PROCESSING : filter ground pointcloud (using multiprocessing)
import os
from multiprocessing import Pool
from produit_derive_lidar.commons import commons
from produit_derive_lidar.filter_one_tile import run_filter_on_tile
import argparse
import logging
from typing import List


def parse_args():
    parser = argparse.ArgumentParser("Generate point cloud filtered by classes.")
    parser.add_argument(
        "--input_dir", "-i",
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
        help="Directory folder for saving the filtered tiles")
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
        help="Classes to keep when filtering. Default: ground + virtual points. " +
        "To provide a list, follow this example : '--keep_classes 2 66 291'"
    )
    parser.add_argument(
        "--cpu_limit",
        type=int,
        default=-1,
        help="Maximum number of cpus to use (Default: use cpu_count - 1)"
    )
    return  parser.parse_args()


def filter_worker(args):
    """Function to pass arguments to run_gf_on_tile as a list (for multiprocessing)
    """
    run_filter_on_tile(*args)


def start_pool(input_dir: str,
               output_dir: str,
               spatial_ref: str="EPSG:2154",
               keep_classes: List=[2, 66],
               cpu_limit: int=-1):
    """Assembles and executes the multiprocessing pool.
    The pre-processing are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(input_dir)
    num_threads = commons.select_num_threads(display_name="ground filtering", cpu_limit=cpu_limit)
    if len(fnames) == 0:
        raise ValueError("No file names were input.")

    pre_map = [[os.path.join(input_dir, fn), output_dir, spatial_ref, keep_classes]
               for fn in fnames]

    with Pool(num_threads) as p:
        p.map(filter_worker, pre_map)
        # Pool close and join are still required when using a context manager
        # cf. https://superfastpython.com/multiprocessing-pool-context-manager/
        p.close()
        p.join()

    logging.info("\nAll workers have returned.")


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    # Create the severals folder if not exists
    os.makedirs(args.output_dir, exist_ok=True)
    start_pool(args.input_dir, args.output_dir,
               spatial_ref=args.spatial_reference,
               keep_classes=args.keep_classes,
               cpu_limit=args.cpu_limit)


if __name__ == '__main__':
    main()