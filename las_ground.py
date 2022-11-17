# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# LAS READING AND FILTER ONLY GROUND
import pdal
import json

def filter_las_ground_withterra(fpath, src, file):
    """ Reads the LAS file and filter only grounds from LIDAR (macro).

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

def filter_las_ground(fpath, src, file):
    """ Reads the LAS file and filter only grounds from LIDAR.

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
                "type": "filters.assign",
                "assignment": "Classification[:]=0"
            },
            {
                "type": "filters.elm",
                "cell": 20,
                "threshold": 2.0,
                "class": 7
            },
            {
                "type": "filters.outlier",
                "mean_k": 10,
                "multiplier": 1
            },
            {
                "type": "filters.smrf",
                "ignore": "Classification[7:7]",
                "slope": 0.12,
                "window": 20,
                "threshold": 0.50,
                "scalar": 0.08
            },
            {
                "type": "filters.range",
                "limits": "Classification[2:2]"
            },
            {
                "type": "filters.iqr",
                "dimension": "Z",
                "k": 9
            },
            {
                "type": "filters.outlier",
                "mean_k": 10,
                "multiplier": 1
            },
            {
                "type": "filters.range",
                "limits": "Classification[2:2]"
            },
            # {
            #     "column": "cls",
            #     "datasource": PATH_SHP,
            #     "dimension": "Classification",
            #     "layer": _ATTRIBUTES,
            #     "type": "filters.overlay",
            #     "query": "SELECT cls FROM attributes where cls=1"
            # },
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