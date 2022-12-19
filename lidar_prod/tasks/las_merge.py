# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Merge the severals LIDAR tiles
import logging
import os
from commons import commons
import pdal
import json


log = logging.getLogger(__name__)


@commons.eval_time
def las_merge(target_folder: str, Listfiles: list):
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
        merge_ground = json.dumps(information, sort_keys=True, indent=4)
        print(merge_ground)
        pipeline = pdal.Pipeline(merge_ground)
        pipeline.execute()
