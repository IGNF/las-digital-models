# RASTER_GENERATION METHODS
import logging

import fiona
import rasterio.mask
from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.raster_clip import clip_raster
import numpy as np
from osgeo import gdal
import rasterio
from rasterio.transform import Affine



def check_raster(fpath):
    """Check if raster has created
    """
    # Check if DTM has created
    ds = gdal.Open(fpath)
    if ds is None:
        return False
    ds = None # Close dataset
    return True


def mask_with_no_data_shapefile(shapefile: str, input_raster: str, output_raster: str, no_data: int):
    """Burn no-data value inside polygons from shapefile (overwrites input raster)
    """
    # # Create raster
    # out = gdal.Rasterize(raster_file, shapefile, allTouched=True, burnValues=no_data)
    # print(out)
    # 1/0
    with fiona.open(shapefile, "r") as fhandle:
        shapes = [feature["geometry"] for feature in fhandle]

    with rasterio.open(input_raster) as src:
        out_image, _ = rasterio.mask.mask(src, shapes,
            crop=False, all_touched=True, invert=True)
        out_meta = src.meta

    with rasterio.open(output_raster, "w", **out_meta) as dest:
        dest.write(out_image)

