# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Merge the severals LIDAR tiles around the tile and raster preparation

import math
import numpy as np
import laspy


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
