# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR PRE-PROCESSING

import argparse
import os
from sys import argv
from gf_processing import start_pool


def parse_args():
    parser = argparse.ArgumentParser("Combine input from ground pointcloud into a single output",
        epilog="Output file will be written to {output}/output")
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
        "--extension", "-e",
        type=str.lower,
        default="las",
        choices=["las", "laz"],
        help="extension")

    return  parser.parse_args()

def create_folder(dest_folder: str):
    """Create the severals folders "DTM" and "_tmp" if not exist"""
    # Create folder "DTM"
    DTM_new_dir = os.path.join(dest_folder, 'DTM')
    if not os.path.isdir(DTM_new_dir):
        os.makedirs(DTM_new_dir)
    # Create folder "_tmp"
    tmp_new_dir = os.path.join(dest_folder, '_tmp')
    if not os.path.isdir(tmp_new_dir):
        os.makedirs(tmp_new_dir)

def main():
    args = parse_args()
    # Create the severals folder if not exists
    create_folder(args.output)
    start_pool(args.input, args.output, filetype=args.extension)

if __name__ == '__main__':
    main()