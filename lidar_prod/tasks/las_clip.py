# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Extract info from the tile
import logging
import os
from commons import commons
import pdal
import json


log = logging.getLogger(__name__)


@commons.eval_time
def las_info(target_folder: str, fname: str):
    """ Launch command "pdal_info --stats" for extracting the bounding box from the LIDAR tile

    Args:
        target_folder (str): directory of pointclouds
        fname (str): name of LIDAR tile

    Returns:
        bounds(tuple) : Tuple of bounding box from the LIDAR tile with buffer (100m)
    """
    # Parameters
    FileInput = os.path.join(target_folder, fname)
    _x = []
    _y = []
    bounds= []
    information = {}
    information = {
    "pipeline": [
            {
                "type": "readers.las",
                "filename": FileInput,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type": "filters.info"
            }
        ]
    }

    # Create json
    json_info = json.dumps(information, sort_keys=True, indent=4)
    print(json_info)
    pipeline = pdal.Pipeline(json_info)
    pipeline.execute()
    pipeline.arrays
    # Extract metadata
    metadata = pipeline.metadata
    if type(metadata) == str:
        metadata = json.loads(metadata)
    # Export bound (maxy, maxy, minx and miny), then creating a buffer with 100 m
    _x.append(float((metadata['metadata']['filters.info']['bbox']['minx']) - 100)) # coordinate minX
    _x.append(float((metadata['metadata']['filters.info']['bbox']['maxx']) + 100)) # coordinate maxX
    _y.append(float((metadata['metadata']['filters.info']['bbox']['miny']) - 100)) # coordinate minY
    _y.append(float((metadata['metadata']['filters.info']['bbox']['maxy']) + 100)) # coordinate maxY
    bounds.append(_x) # [xmin, xmax]
    bounds.append(_y) # insert [ymin, ymax]
    return tuple(i for i in bounds)

@commons.eval_time
def las_crop(target_folder: str, src: str, fname: str):
    """ Crop filter removes points that fall inside a cropping bounding box (2D) (with buffer 100 m)

    Args:
        target_folder (str): directory of pointclouds
        src (str): directory of pointclouds
        fname (str): name of LIDAR tile
    """
    # Lauch las_info for extracting boudning box
    bounds = str(las_info(target_folder, fname))
    # Parameters
    root = os.path.splitext(fname)[0]
    FileInput = os.path.join(src, "_tmp", f'{root}_merge.las')
    FileOutput = os.path.join(src, "_tmp", f'{root}_crop.las')
    information = {}
    information = {
    "pipeline": [
            {
                "type": "readers.las",
                "filename": FileInput,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type":"filters.crop",
                "bounds": bounds
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
    # Create json
    json_crop = json.dumps(information, sort_keys=True, indent=4)
    print(json_crop)
    pipeline = pdal.Pipeline(json_crop)
    pipeline.execute()
