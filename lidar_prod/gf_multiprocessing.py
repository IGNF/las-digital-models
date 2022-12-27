# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR PRE-PROCESSING : filter ground pointcloud (using multiprocessing)
from commons import commons
import os
from multiprocessing import Pool, cpu_count
from gf_one_tile import run_gf_on_tile
import argparse


CPU_LIMIT=int(os.getenv("CPU_LIMIT", "-1"))


def parse_args():
    parser = argparse.ArgumentParser("Combine input from ground pointcloud into a single output")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="input folder (most likely the same as the one you used with PDAL folder 'data')")
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Directory folder for saving the outputs")
    parser.add_argument(
        "--temp_dir", "-t",
        type=str,
        default = "/tmp",
        help="Directory folder for saving the outputs")
    parser.add_argument(
        "--extension", "-e",
        type=str.lower,
        default="las",
        choices=["las", "laz"],
        help="extension")

    return  parser.parse_args()


def gf_worker(args):
    """Function to pass arguments to run_gf_on_tile as a list (for multiprocessing)
    """
    run_gf_on_tile(*args)


def start_pool(input_dir: str, output_dir: str, temp_dir: str, filetype = 'las'):
    """Assembles and executes the multiprocessing pool.
    The pre-processing are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(input_dir, filetype)
    cores = cpu_count()
    print(f"Found {cores} logical cores in this PC")
    num_threads = cores -1
    if CPU_LIMIT > 0 and num_threads > CPU_LIMIT:
        print(f"Limit CPU usage to {CPU_LIMIT} cores due to env var CPU_LIMIT")
        num_threads = CPU_LIMIT
    print("\nStarting ground filtering pool of processes on the {}".format(
        num_threads) + " logical cores.\n")
    if len(fnames) == 0:
        print("Error: No file names were input. Returning."); return

    pre_map = [[os.path.join(input_dir, fn), output_dir] for fn in fnames]

    with Pool(num_threads) as p:
        p.map(gf_worker, pre_map)

    print("\nAll workers have returned.")


def main():
    args = parse_args()
    # Create the severals folder if not exists
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.temp_dir, exist_ok=True)
    start_pool(args.input, args.output, args.temp_dir, filetype=args.extension)


if __name__ == '__main__':
    main()