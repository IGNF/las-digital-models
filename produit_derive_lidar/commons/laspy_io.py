# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Merge the severals LIDAR tiles around the tile and raster preparation

import math
import numpy as np
import laspy


def read_las_file_to_numpy(input_file):
    """Takes the filepath to an input LAS (crop) file and the desired output raster cell size
    Reads the LAS file and outputs the ground points as a numpy array.
    Also establishes some asic raster parameters:
    - the extents
    - the raster shape (sometimes resolution)
    - the coordinate location of the relative origin (bottom left)
        """
    in_file = laspy.read(input_file)
    in_np = np.vstack((in_file.x, in_file.y, in_file.z)).transpose()

    return in_np
