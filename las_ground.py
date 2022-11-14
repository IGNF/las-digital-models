# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# LAS READING AND FILTER ONLY GROUND
import pdal
import json

def las_ground(fpath, src, file):
    """ Reads the LAS file and filter only grounds
    the ground points.

    Args:
        fpath (str) : directory of projet who contains LIDAR (Ex. "data")
        src (str): directory of work who contains the code
        file (str): name of LIDAR tiles
    """
    dst = str("DTM".join([src, '/']))
    FileOutput = "".join([dst, "_".join([file[:-4], 'ground.las'])])
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
                "a_srs": "EPSG:2154",
                # "minor_version": 4,
                # "dataformat_id": 6,
                "filename": FileOutput
            }
        ]
    }
    ground = json.dumps(information, sort_keys=True, indent=4)
    print(ground)
    pipeline = pdal.Pipeline(ground)
    pipeline.execute()