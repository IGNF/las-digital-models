# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Clip raster with bouding box
import pdal
import numpy as np
from osgeo import gdal
import json
from tasks.las_clip import las_info


def las_info(target_folder, fname):
    """ target_folder, fname
    Launch command "pdal_info --stats" for extracting the bounding box from the LIDAR tile

    Args:
        target_folder (str): directory of pointclouds
        fname (str): name of LIDAR tile

    Returns:
        bounds(tuple) : Tuple of bounding box from the LIDAR tile with buffer (100m)
    """
    # Parameters
    FileInput = str("".join([target_folder, fname]))
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
    # Extract maxy, maxy, minx and miny
    minx = float((metadata['metadata']['filters.info']['bbox']['minx'])) # coordinate minX
    maxx = float((metadata['metadata']['filters.info']['bbox']['maxx'])) # coordinate maxX
    miny = float((metadata['metadata']['filters.info']['bbox']['miny'])) # coordinate minY
    maxy = float((metadata['metadata']['filters.info']['bbox']['maxy'])) # coordinate maxY
    return minx, miny, maxx, maxy

def clip_raster(target_folder, temp_folder, src, fname, size, _size, method):
    """ Clip the rasters with the boudnign box

    Args:
        target_folder (str): directory of pointclouds
        tmp_folder (str): directory "_tmp"
        src (str) : directory "DTM"
        fname (str): name of LIDAR tile
        size (str): raster cell size
        n_size (str): resolution from raster for output's name
        method (str): interpolation method

    """
    # Extract the bounding box
    coordinates = las_info(target_folder, fname)
    minX = coordinates[0]
    minY = coordinates[1]
    maxX = coordinates[2]
    maxY = coordinates[3]
    # Parameters
    InputImage = str(fname[:-4].join([temp_folder, "".join([_size, method])]))
    OutputImage = str(fname[:-4].join([src, "".join([_size, method])]))
    RasterFormat = 'GTiff'
    PixelRes = float(size)
    # Open datasets
    Raster = gdal.Open(InputImage, gdal.GA_ReadOnly)
    Projection = Raster.GetProjectionRef()
    # Create raster
    OutTile = gdal.Warp(OutputImage, Raster, format=RasterFormat, outputBounds=[minX, minY, maxX, maxY], xRes=PixelRes, yRes=PixelRes, dstSRS=Projection, resampleAlg=gdal.GRA_NearestNeighbour, options=['COMPRESS=DEFLATE'])
    OutTile = None # Close dataset