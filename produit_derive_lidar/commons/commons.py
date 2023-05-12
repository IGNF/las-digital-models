# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# COMMONS
import logging
from multiprocessing import cpu_count
import os
import time
from typing import Callable
import sys


def select_num_threads(display_name="", cpu_limit=-1):
    """Select number of threads for multiprocessing from the number of cpu core and cpu_limit
    (maximum number of cores to use)"""
    cores = cpu_count()
    logging.info(f"Found {cores} logical cores in this PC")
    num_threads = cores -1
    if cpu_limit > 0 and num_threads > cpu_limit:
        logging.info(f"Limit CPU usage to {cpu_limit} cores.")
        num_threads = cpu_limit
    logging.info(f"\nStarting {display_name} pool of processes on the {num_threads} logical cores.\n")

    return num_threads


def get_logger(name):
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.INFO)
    log.addHandler(streamHandler)

    return log


def eval_time(function: Callable):
    """decorator to log the duration of the decorated method"""

    def timed(*args, **kwargs):
        time_start = time.time()
        result = function(*args, **kwargs)
        time_elapsed = round(time.time() - time_start, 2)

        logging.info(f"Processing time of {function.__name__}: {time_elapsed}s")
        return result

    return timed


def eval_time_with_pid(function: Callable):
    """decorator to log the duration of the decorated method"""

    def timed(*args, **kwargs):
        logging.info(f"Starting {function.__name__} with PID {os.getpid()}.")
        time_start = time.time()
        result = function(*args, **kwargs)
        time_elapsed = round(time.time() - time_start, 2)
        logging.info(f"{function.__name__} with PID {os.getpid()} finished.")
        logging.info(f"Processing time of {function.__name__}: {time_elapsed}s")
        return result

    return timed


def listPointclouds(folder: str):
    """ Return list of pointclouds in the folder 'data'

    Args:
        folder (str): 'data' directory who contains severals pointclouds (tile)
        filetype (str): pointcloud's type in folder 'data : LAS or LAZ ?

    Returns:
        li(List): List of pointclouds (name)
    """
    li = [f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lstrip(".").lower() in point_cloud_extensions]

    return li


def give_name_resolution_raster(size):
    """
    Give a resolution from raster

    Args:
        size (int): raster cell size

    Return:
        _size(str): resolution from raster for output's name
    """
    size_cm = size * 100
    if int(size) == float(size):
        _size = f"_{int(size)}M"
    elif int(size_cm) == float(size_cm):
        _size = f"_{int(size_cm)}CM"
    else :
        raise ValueError(f"Cell size ({size}) has a precision smaller than centimeters: " +
                         "output name not implemented for this case")

    return _size