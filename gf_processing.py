# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# PRE-PROCESSING : filter ground pointcloud

import os
from multiprocessing import Pool, cpu_count
from las_ground import filter_las_ground_withterra, filter_las_ground


def listPointclouds(folder, filetype):
    """ Return list of pointclouds in the folder 'data'

    Args:
        folder (str): 'data' directory who contains severals pointclouds (tile)
        filetype (str): pointcloud's type in folder 'data : LAS or LAZ ?

    Returns:
        li(List): List of pointclouds (name)
    """      
    li = []
    f = os.listdir(folder)
    for e in f:
        extension = e.rpartition('.')[-1]
        if extension in filetype:
            li.append(e)
    return li

def ip_worker(mp):
    """Multiprocessing worker function to be used by the
    p.map function to map objects to, and then start
    multiple times in parallel on separate CPU cores.
    In this case the worker function instances prepare
    one file each, writing the resulting merge LIDAR.
    """
    # Parameters
    fpath = (mp[0] + mp[2])[:-3] + mp[3]
    fname = mp[2]
    src = mp[1]
    # Filter pointcloud from TerraSolid : keep only ground 
    filter_las_ground_withterra(fpath, src, fname)
    # Filter pointcloud  : keep only ground 
    #filter_las_ground(fpath, src, fname)


def start_pool(target_folder, src, filetype = 'las'):
    """Assembles and executes the multiprocessing pool.
    The pre-processing are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = listPointclouds(target_folder, filetype)
    cores = cpu_count()
    print("\nStarting interpolation pool of processes on the {}".format(
        cores) + " logical cores found in this PC.\n")
    if cores < len(fnames):
        print("Warning: more processes in pool than processor cores.\n" +
              "Optimally, roughly as many processes as processor " +
              "cores should be run concurrently.\nYou are starting " +
              str(len(fnames)) + " processes on " + str(cores) + " cores.\n")
    elif len(fnames) == 0:
        print("Error: No file names were input. Returning."); return
    pre_map, processno = [], len(fnames)
    for i in range(processno):
        pre_map.append([target_folder, src, fnames[i].strip('\n'), filetype])
    p = Pool(cores -1)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
