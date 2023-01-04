# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR INTERPOLATION + POST-PROCESSING
#             PRIMARY ENTRY POINT FOR PROGRAM

import argparse
from commons import commons
from multiprocessing import Pool
import os
from ip_one_tile import run_ip_on_tile


def parse_args():
    parser = argparse.ArgumentParser("Main script for interpolation + post-processing",
        epilog="""All IDW parameters are optional, but it is assumed the user will fine-tune them,
hence the defaults are not listed.
Output files will be written to the target folder, tagged with thename of the interpolation method
that was used.
The number of parallel processes can be limited using the CPU_COUNT environment variable """)
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
    # Optional arguments for IDW
    # Not used at the moment
    # parser.add_argument(
    #     "--idw_radius",
    #     type=float,
    #     required=False,
    #     help="IDW radius (for PDAL-IDW) " +
    #          "// STARTING IDW radius/number of neighbours to query (for IDWquad)")
    # parser.add_argument(
    #     "--idw_power",
    #     type=float,
    #     required=False,
    #     help="IDW power (for PDAL-IDW and IDWquad)")
    # parser.add_argument(
    #     "--idw_kernel_width",
    #     type=float,
    #     required=False,
    #     help="IDW fallback kernel width (for PDAL-IDW)" +
    #          "MINIMUM number of points per quadrant (for IDWquad)")
    # parser.add_argument(
    #     "--increment",
    #     type=float,
    #     required=False,
    #     help="radius/number of neighbours INCREMENT value (for IDWquad)")
    # parser.add_argument(
    #     "--idwquad_method",
    #     type=str,
    #     required=False,
    #     choices=["radial", "k-nearest"],
    #     help="IDWquad method")
    # parser.add_argument(
    #     "--idwquad_tolerence",
    #     type=float,
    #     required=False,
    #     help="IDWquad method")
    # parser.add_argument(
    #     "--idwquad_iterations",
    #     type=float,
    #     required=False,
    #     help="IDWquad maximum number of iteration before declaring no-data")

    return  parser.parse_args()


def ip_worker(args):
    """Function to pass arguments to run_ip_on_tile as a list (for multiprocessing)
    """
    run_ip_on_tile(*args)


def start_pool(input_dir, output_dir, temp_dir='/tmp', filetype='las', postprocess=0,
               size = 1, method = 'startin-Laplace'):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(input_dir, filetype)
    num_threads = commons.select_num_threads(display_name="interpolation")

    if len(fnames) == 0:
        print("Error: No file names were input. Returning.")
        return

    pre_map = [[os.path.join(input_dir, fn), temp_dir, output_dir, size, method, postprocess]
               for fn in fnames]
    with Pool(num_threads) as p:
        p.map(ip_worker, pre_map)
        # Pool close and join are still required when using a context manager
        # cf. https://superfastpython.com/multiprocessing-pool-context-manager/
        p.close()
        p.join()


    print("\nAll workers have returned.")


def main():
    args = parse_args()
    # Create the severals folder if not exists
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.temp_dir, exist_ok=True)
    start_pool(args.input, args.output, args.temp_dir, filetype=args.extension,
               postprocess=args.postprocessing, size=args.pixel_size,
               method=args.interpolation_method)


if __name__ == '__main__':
    main()