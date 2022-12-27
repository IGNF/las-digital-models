# RASTER_GENERATION METHODS

from commons import commons
import os
from time import time
from multiprocessing import Pool, cpu_count
import numpy as np
from osgeo import gdal
from tasks.raster_clip import clip_raster


def write_geotiff_withbuffer(raster, origin, size, fpath):
    """Writes the interpolated TIN-linear and Laplace rasters
    to disk using the GeoTIFF format with buffer (100 m). The header is based on
    the raster array and a manual definition of the coordinate
    system and an identity affine transform.

    Args:
        raster(array) : Z interpolation
        origin(list): coordinate location of the relative origin (bottom left)
        size (float): raster cell size
        fpath(str): path to the output geotiff file

    Returns:
        bool: If the output "DTM" saved in fpath is okay or not
    """
    import rasterio
    from rasterio.transform import Affine
    transform = (Affine.translation(origin[0], origin[1])
                 * Affine.scale(size, size))
    with rasterio.Env():
        with rasterio.open(fpath, 'w', driver = 'GTiff',
                           height = raster.shape[0],
                           width = raster.shape[1],
                           count = 1,
                           dtype = rasterio.float32,
                           crs='EPSG:2154',
                           transform = transform
                           ) as out_file:
            out_file.write(raster.astype(rasterio.float32), 1)


def check_raster(fpath):
    """Check if raster has created
    """
    # Check if DTM has created
    ds = gdal.Open(fpath)
    if ds is None:
        return False
    ds = None # Close dataset
    return True


def patch(raster, res, origin, size, min_n):
    """Patches in missing pixel values by applying a median
    kernel (3x3) to estimate its value. This is meant to serve
    as a means of populating missing pixels, not as a means
    of interpolating large areas. The last parameter should
    be an integer that specifies the minimum number of valid
    neighbour values to fill a pixel (0 <= min_n <= 8).

    Args:
        raster(array) : Z interpolation
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
        size (float): raster cell size
        min_n(float): minimum number of valid neighbour values
    """
    mp = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
          [0, 1], [1, -1], [1, 0], [1, 1]]
    for yi in range(res[1]):
        for xi in range(res[0]):
            if raster[yi, xi] == -9999:
                vals = []
                for m in range(8):
                    xw, yw = xi + mp[m][0], yi + mp[m][1]
                    if (xw >= 0 and xw < res[0]) and (yw >= 0 and yw < res[1]):
                        val = raster[yw, xw]
                        if val != -9999: vals += [val]
                if len(vals) > min_n: raster[yi, xi] = np.median(vals)


@commons.eval_time_with_pid
def export_raster(las_file, ras, origin, size, geotiff_path_temp, geotiff_path, method):
    """Write raster in the folder DTM with clipping from the LIDAR tile"""
    if method in ['startin-TINlinear', 'startin-Laplace', 'CGAL-NN', 'IDWquad']:
        write_geotiff_withbuffer(ras, origin, size, geotiff_path_temp)

    if check_raster(geotiff_path_temp) == True:
        clip_raster(las_file, geotiff_path_temp, geotiff_path, size)