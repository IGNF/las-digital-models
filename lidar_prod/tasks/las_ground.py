# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# LAS READING AND FILTER ONLY GROUND
import logging
import os
from commons import commons
import pdal
import json


log = logging.getLogger(__name__)


@commons.eval_time
def filter_las_ground(input_file: str, output_file: str):
    """ Reads the LAS file and filter only grounds from LIDAR.

    Args:
        fileInput (str) : Path to the input lidar file
        folderOutput (str): Path to the output directory
    """
    root = os.path.splitext(os.path.basename(input_file))[0]
    information = {}
    information = {
    "pipeline": [
            {
                "type":"readers.las",
                "filename":input_file,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type":"filters.range",
                "limits":"Classification[2:2],Classification[66:66]"
            },
            {
                "type": "writers.las",
                "a_srs": "EPSG:2154",
                # "minor_version": 4,
                # "dataformat_id": 6,
                "filename": output_file
            }
        ]
    }
    ground = json.dumps(information, sort_keys=True, indent=4)
    print(ground)
    pipeline = pdal.Pipeline(ground)
    pipeline.execute()
