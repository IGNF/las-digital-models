# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# Clip raster with bouding box
from pdaltools.las_info import parse_filename
from osgeo import gdal
from produit_derive_lidar.commons import commons


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
    _, coordX, coordY, _ = parse_filename(input_las)
    coordX = float(coordX)
    coordY = float(coordY)
    # Coordinates in the filenames are x_min and y_max
    minX = coordX * commons.tile_coord_scale - PixelRes/2
    maxX = coordX * commons.tile_coord_scale - PixelRes/2 + commons.tile_width
    maxY = coordY * commons.tile_coord_scale + PixelRes/2
    minY = coordY * commons.tile_coord_scale + PixelRes/2 - commons.tile_width

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