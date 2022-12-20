# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# PRE-PROCESSING : filter ground pointcloud
import os
from multiprocessing import Pool, cpu_count
from tasks.las_ground import filter_las_ground

CPU_LIMIT=int(os.getenv("CPU_LIMIT", "-1"))

def listPointclouds(folder: str, filetype: str):
    """ Return list of pointclouds in the folder 'data'

    Args:
        folder (str): 'data' directory who contains severals pointclouds (tile)
        filetype (str): pointcloud's type in folder 'data : LAS or LAZ ?

    Returns:
        li(List): List of pointclouds (name)
    """
    li = [f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lstrip(".").lower() == filetype]

    return li

def ip_worker(mp):
    """Multiprocessing worker function to be used by the
    p.map function to map objects to, and then start
    multiple times in parallel on separate CPU cores.
    In this case the worker function instances prepare
    one file each, writing the resulting merge LIDAR.
    Args:
        mp: list of arguments : [input_dir, output_dir, temp_dir, fname, filetype]
    """
    # Parameters
    input_dir, output_dir, fname = mp

    # Filter pointcloud : keep only ground and virtual points if exist
    tile_name = os.path.splitext(fname)[0]
    output_file = os.path.join(output_dir, f"{tile_name}_ground.las")
    filter_las_ground(os.path.join(input_dir, fname), output_file)


def start_pool(input_dir: str, output_dir: str, temp_dir: str, filetype = 'las'):
    """Assembles and executes the multiprocessing pool.
    The pre-processing are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = listPointclouds(input_dir, filetype)
    cores = cpu_count()
    print(f"Found {cores} logical cores in this PC")
    num_threads = cores -1
    if CPU_LIMIT > 0 and num_threads > CPU_LIMIT:
        print(f"Limit CPU usage to {CPU_LIMIT} cores due to env var CPU_LIMIT")
        num_threads = CPU_LIMIT
    print("\nStarting interpolation pool of processes on the {}".format(
        num_threads) + " logical cores.\n")
    if len(fnames) == 0:
        print("Error: No file names were input. Returning."); return
    pre_map, processno = [], len(fnames)
    for i in range(processno):
        pre_map.append([input_dir, output_dir, fnames[i]])
    p = Pool(num_threads)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
