# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR PRE-PROCESSING

import argparse
import os
from sys import argv
from gf_processing import start_pool


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


def main():
    args = parse_args()
    # Create the severals folder if not exists
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.temp_dir, exist_ok=True)
    start_pool(args.input, args.output, args.temp_dir, filetype=args.extension)


if __name__ == '__main__':
    main()