# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Extract info from the tile
import logging
from commons import commons
import pdal
import json


log = logging.getLogger(__name__)


@commons.eval_time
def las_crop(input_file: str, output_file: str, bounds):
    """ Crop filter removes points that fall inside a cropping bounding box (2D)
    Args:
        input_dir (str): input point cloud file
        output_dir (str): output point cloud file
        bounds : 2D bounding box to crop to
    """
    # Parameters
    information = {
    "pipeline": [
            {
                "type": "readers.las",
                "filename": input_file,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type":"filters.crop",
                "bounds": str(bounds)
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
    # Create json
    json_crop = json.dumps(information, sort_keys=True, indent=4)
    print(json_crop)
    pipeline = pdal.Pipeline(json_crop)
    pipeline.execute()
