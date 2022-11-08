# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Merge the severals LIDAR tiles
import os
import math
import numpy as np
import pdal
import laspy
import json

def las_merge(target_folder, Listfiles):
    """Merge ground pointcloud to folder 'output"

    Args:
        target_folder (str): directory of pointclouds
        Listfiles(list): List of ground pointclouds and the output file
    """
    Fileoutput = str("output/".join([target_folder[:-5], 'merge_ground.las']))
    # Create folder 'output' if not exist
    if os.path.isdir('./output') is False:
        os.makedirs('output')
    if not os.path.exists(Fileoutput):
        information = {}
        information = {
        "pipeline": 
                Listfiles
        }
        ground = json.dumps(information, sort_keys=True, indent=4)
        pipeline = pdal.Pipeline(ground)
        pipeline.execute()
