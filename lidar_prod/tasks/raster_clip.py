# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Clip raster with bouding box
from lidar_prod.commons import commons
from osgeo import gdal


def clip_raster(input_las, input_image, output_image, size):
    """ Clip the rasters with the boudnign box

    Args:
        input_file (str): input_pointcloud
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
    RasterFormat = 'GTiff'
    PixelRes = float(size)
    # Open datasets
    Raster = gdal.Open(input_image, gdal.GA_ReadOnly)
    Projection = Raster.GetProjectionRef()
    # Create raster
    OutTile = gdal.Warp(output_image, Raster,
        format=RasterFormat,
        outputBounds=[minX, minY, maxX, maxY],
        xRes=PixelRes,
        yRes=PixelRes,
        dstSRS=Projection,
        resampleAlg=gdal.GRA_NearestNeighbour,
        options=['COMPRESS=DEFLATE'])
    OutTile = None # Close dataset