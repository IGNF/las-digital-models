# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# LAS READING AND RASTER PREPARATION
import os
import math
import numpy as np
import pdal
import laspy
import json

def las_prepare(size, fpath):
    """Takes the filepath to an input LAS file and the
    desired output raster cell size. Reads the LAS file and outputs
    the ground points as a numpy array. Also establishes some
    basic raster parameters:
        - the extents
        - the resolution in coordinates
        - the coordinate location of the relative origin (bottom left)

    Args:
        size (int): raster cell size
        fpath (str): directory of pointcloud
    
    Returns:
        extents(array) : extents
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
    """
    #in_file = File(fpath, mode = "r")
    # with open(target_folder + "config_preprocess.json", 'r') as file_in:
    #     preconfig = file_in.read()
    # config = ('[\n\t"' + fpath + '",\n' + preconfig +
    #             ',\n\t\t"type": "' + "writes.las" +
    #             ',\n\t\t"filename": "' + fpath[:-4] + '_ground.las"\n\t}\n]')
    Fileoutput = "_".join([fpath[:-4], 'ground.las'])
    information = {}
    information = {
       "pipeline": [
            {
                "type":"readers.las",
                "filename":fpath,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type":"filters.range",
                "limits":"Classification[2:2]"
            },
            {
                "type": "writers.las",
                "filename": Fileoutput
            }
        ]
    }
    # ground = json.dumps(information, sort_keys=True, indent=4)
    # pipeline = pdal.Pipeline(ground)
    # pipeline.execute()
    in_file = laspy.read((fpath[:-4] + '_ground.las'))
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