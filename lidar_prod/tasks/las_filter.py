# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# LAS READING AND FILTER BY CLASSES (GROUND + VIRTUAL POINTS BY DEFAULT)
import json
from lidar_prod.commons import commons
import logging
import os

import pdal
from typing import List


@commons.eval_time_with_pid
def filter_las_classes(input_file: str,
                       output_file: str,
                       spatial_ref: str="EPSG:2154",
                       keep_classes: List=[2, 66]):
    """ Reads the LAS file and filter only grounds from LIDAR.

    Args:
        fileInput (str) : Path to the input lidar file
        spatial_ref (str) : spatial reference to use when reading the las file
        output_file (str): Path to the output file
        keep_classes (List): Classes to keep in the filter (ground + virtual points by default)
    """
    limits = ",".join(f"Classification[{c}:{c}]" for c in keep_classes)
    information = {}
    information = {
    "pipeline": [
            {
                "type":"readers.las",
                "filename": input_file,
                "override_srs": spatial_ref,
                "nosrs": True
            },
            {
                "type":"filters.range",
                "limits": limits
            },
            {
                "type": "writers.las",
                "a_srs": spatial_ref,
                # "minor_version": 4,
                # "dataformat_id": 6,
                "filename": output_file
            }
        ]
    }
    ground = json.dumps(information, sort_keys=True, indent=4)
    logging.info(ground)
    pipeline = pdal.Pipeline(ground)
    pipeline.execute()
