# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Merge the severals LIDAR tiles around the tile and raster preparation

import math
import numpy as np
import laspy
from las_stitching.las_add_buffer import create_las_with_buffer


def read_las_file_to_numpy(input_file, size):
    """Takes the filepath to an input LAS (crop) file and the desired output raster cell size
    Reads the LAS file and outputs the ground points as a numpy array.
    Also establishes some asic raster parameters:
    - the extents
    - the resolution in coordinates
    - the coordinate location of the relative origin (bottom left)
        """
    in_file = laspy.read(input_file)
    header = in_file.header
    in_np = np.vstack((in_file.raw_classification,
                           in_file.x, in_file.y, in_file.z)).transpose()
    in_np = in_np[in_np[:,0] == 2].copy()[:,1:]
    extents = [[header.min[0], header.max[0]],
               [header.min[1], header.max[1]]]
    res = [math.ceil((extents[0][1] - extents[0][0]) / size),
           math.ceil((extents[1][1] - extents[1][0]) / size)]
    origin = [np.mean(extents[0]) - (size / 2) * res[0],
              np.mean(extents[1]) - (size / 2) * res[1]]
    return in_np, res, origin


def las_prepare(input_dir: str, input_file: str, merge_file: str, output_file: str, size: float,
                spatial_ref="EPSG:2154", buffer_width=100):
    """Severals steps :
        1- Create tile with buffer
        2- Read the new tile and establish basic raster parameter (ct read_las_file_to_numpy)

    Args:
        input_dir (str): directory of pointclouds
        input_file (str): full path of pointcloud to prepare
        merge_file (str): full path to intermediate result tile (tile merged qith its 8 neighbors)
        output_file (str): full path of returned prepared pointcloud
        size (int): raster cell size

    Returns:
        extents(array) : extents
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
    """
    # Parameters


    create_las_with_buffer(input_dir, input_file, merge_file, output_file,
                           buffer_width=buffer_width,
                           spatial_ref=spatial_ref)
    in_np, res, origin = read_las_file_to_numpy(output_file, size)

    return in_np, res, origin