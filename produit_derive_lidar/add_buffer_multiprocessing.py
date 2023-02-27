import argparse
from produit_derive_lidar.commons import commons
from pdaltools.las_add_buffer import create_las_with_buffer
import logging
from multiprocessing import Pool
import os


def parse_args():
    parser = argparse.ArgumentParser("Main script for buffer addition to a las file")
    parser.add_argument(
        "--input_dir", "-i",
        type=str,
        required=True,
        help="Path to the the folder containing the tile to which you want to add buffer"
    )
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        required=True,
        help="Directory folder for saving the outputs"
    )
    parser.add_argument(
        "--buffer_width", "-b",
        default=100,
        type=int,
        help="Width (in meter) for the buffer that is added to the tile before interpolation " +
             "(to prevent artefacts)"
    )
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
    create_las_with_buffer(*args)


def start_pool(input_dir: str,
               output_dir: str,
               buffer_width=100,
               spatial_ref="EPSG:2154",
               cpu_limit: int=-1,
               ):
    """Assembles and executes the multiprocessing pool.
    """
    fnames = commons.listPointclouds(input_dir)
    num_threads = commons.select_num_threads(display_name="add_buffer", cpu_limit=cpu_limit)

    if len(fnames) == 0:
        raise ValueError("No file names were input")

    pre_map = [[input_dir, os.path.join(input_dir, fn),
                os.path.join(output_dir, fn), buffer_width, spatial_ref]
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
    start_pool(input_dir=args.input_dir,
               output_dir=args.output_dir,
               buffer_width=args.buffer_width,
               spatial_ref=args.spatial_reference,
               cpu_limit=args.cpu_limit,
    )


if __name__ == '__main__':
    main()