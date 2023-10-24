# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Merge the severals LIDAR tiles around the tile and raster preparation

from typing import Tuple

import laspy
import numpy as np


def read_las_and_extract_points_and_classifs(input_file: str) -> Tuple[laspy.lasdata.LasData, np.array, np.array]:
    """Read las file with laspy and extract points coordinates and classifications

    Args:
        input_file (str): path to las file

    Returns:
        Tuple[laspy.lasdata.LasData, np.array, np.array]:
            las: las file object (laspy)
            pcd: points coordinates as an array of shape (nb_points, 3)
            classigs : points classifications as an array of shape (nb_points)
    """
    las = laspy.read(input_file)
    pcd = np.vstack((las.x, las.y, las.z)).transpose()
    classifs = np.copy(las.classification)

    return las, pcd, classifs
