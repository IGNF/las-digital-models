# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Clip raster with bouding box
from commons import commons
import os
from osgeo import gdal


def clip_raster(input_dir, temp_folder, output_dir, fname, size, _size, method_postfix):
    """ Clip the rasters with the boudnign box

    Args:
        input_dir (str): directory of pointclouds
        tmp_folder (str): directory "_tmp"
        output_dir (str) : directory "DTM"
        fname (str): name of LIDAR tile
        size (str): raster cell size
        n_size (str): resolution from raster for output's name
        method_postfix (str): interpolation method name (for file naming)

    """
    # Extract the bounding box
    (minX, maxX), (minY, maxY) = commons.las_info(input_las, buffer_width=0)
    # Parameters
    root = os.path.splitext(fname)[0]
    InputImage = os.path.join(temp_folder, f"{root}{_size}_{method_postfix}.tif")
    OutputImage = os.path.join(output_dir, f"{root}{_size}_{method_postfix}.tif")
    RasterFormat = 'GTiff'
    PixelRes = float(size)
    # Open datasets
    Raster = gdal.Open(InputImage, gdal.GA_ReadOnly)
    Projection = Raster.GetProjectionRef()
    # Create raster
    OutTile = gdal.Warp(OutputImage, Raster,
        format=RasterFormat,
        outputBounds=[minX, minY, maxX, maxY],
        xRes=PixelRes,
        yRes=PixelRes,
        dstSRS=Projection,
        resampleAlg=gdal.GRA_NearestNeighbour,
        options=['COMPRESS=DEFLATE'])
    OutTile = None # Close dataset