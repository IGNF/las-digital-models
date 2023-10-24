# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# COMMONS
import logging
import os
import sys
import time
from typing import Callable


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
    else:
        raise ValueError(
            f"Cell size is subcentimetric ({size}m) i.e raster resolution is "
            + "too high : output name not implemented for this case"
        )

    return _size
