# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# INTERPOLATION + POST-PROCESSING SCRIPTS

import os
from time import time
from multiprocessing import Pool, cpu_count
import numpy as np
from osgeo import gdal
from tasks.las_prepare import las_prepare
from tasks.raster_clip import clip_raster
from tasks.las_interpolation_deterministic import deterministic_method

CPU_LIMIT=int(os.getenv("CPU_LIMIT", "-1"))

def give_name_resolution_raster(size):
    """
    Give a resolution from raster

    Args:
        size (int): raster cell size

    Return:
        _size(str): resolution from raster for output's name
    """
    if float(size) == 1.0:
        _size = str('_1M')
    elif float(size) == 0.5:
        _size = str('_50CM')
    elif float(size) == 5.0:
        _size = str('_5M')
    else:
        _size = str(size)
    return _size

def write_geotiff_withbuffer(raster, origin, size, fpath):
    """Writes the interpolated TIN-linear and Laplace rasters
    to disk using the GeoTIFF format with buffer (100 m). The header is based on
    the raster array and a manual definition of the coordinate
    system and an identity affine transform.

    Args:
        raster(array) : Z interpolation
        origin(list): coordinate location of the relative origin (bottom left)
        size (float): raster cell size
        fpath(str): target folder "_tmp"

    Returns:
        bool: If the output "DTM" in the folder "_tmp" is okay or not
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

def ip_worker(mp):
    """Multiprocessing worker function to be used by the
    p.map function to map objects to, and then start
    multiple times in parallel on separate CPU cores.
    In this case the worker function instances interpolate
    one file each, writing the resulting rasters to disk.
    Runs slightly different workflows depending on the
    desired interpolation method/export format.
    """
    # Parameters
    src, target_folder, postprocess = mp[0], mp[3], mp[1]
    size, fpath = mp[2], ("_tmp/".join([mp[0], mp[4][:-4]]))
    fname, method = mp[4], mp[5]
    # Extract coordinate, resolution and coordinate location of the relative origin
    print("PID {} starting to work on {}".format(os.getpid(), fname))
    start = time()
    gnd_coords, res, origin = las_prepare(target_folder, src, fname, size)
    # Interpolation with method deterministic
    _interpolation = deterministic_method(gnd_coords, res, origin, size, method)
    ras = _interpolation.run(target_folder=mp[3], fname=mp[4])
    end = time()
    print("PID {} finished interpolating.".format(os.getpid()),
          "Time spent interpolating: {} sec.".format(round(end - start, 2)))
    # if postprocess > 0:
    #     start = time
    #     print("PID {} finished post-processing.".format(os.getpid()),
    #           "Time spent post-processing: {} sec.".format(
    #               round(end - start, 2)))
    # Return size for output's name
    _size = give_name_resolution_raster(size)
    # Write raster in the folder DTM who clipping from the LIDAR tile
    start = time()
    if method == 'startin-TINlinear':
        write_geotiff_withbuffer(ras, origin, size, fpath + _size + '_TINlinear.tif')
        if check_raster(fpath + _size + '_TINlinear.tif') == True:
            clip_raster(target_folder, "_tmp".join([src, "/"]), "DTM".join([src, "/"]), fname, size, _size, '_TINlinear.tif')
    if method == 'startin-Laplace':
        write_geotiff_withbuffer(ras, origin, size, fpath + _size + '_Laplace.tif')
        if check_raster(fpath + _size + '_Laplace.tif') == True:
            clip_raster(target_folder, "_tmp".join([src, "/"]), "DTM".join([src, "/"]), fname, size, _size, '_Laplace.tif')
    if method == 'CGAL-NN':
        write_geotiff_withbuffer(ras, origin, size, fpath + _size + '_NN.tif')
        if check_raster(fpath + _size + '_NN.tif') == True:
            clip_raster(target_folder, "_tmp".join([src, "/"]), "DTM".join([src, "/"]), fname, size, _size, '_NN.tif')
    if method == 'IDWquad':
        write_geotiff_withbuffer(ras, origin, size, fpath + _size + '_IDWquad.tif')
        if check_raster(fpath + _size + '_IDWquad.tif') == True:
            clip_raster(target_folder, "_tmp".join([src, "/"]), "DTM".join([src, "/"]), fname, size, _size, '_IDWquad.tif')
    if method == 'PDAL-IDW':
        if check_raster(fpath + _size + '_IDW.tif') == True:
            clip_raster(target_folder, "_tmp".join([src, "/"]), "DTM".join([src, "/"]), fname, size, _size, '_IDW.tif')
    end = time()
    print("PID {} finished exporting.".format(os.getpid()),
          "Time spent exporting: {} sec.".format(round(end - start, 2)))

def listPointclouds(folder, filetype):
    """ Return list of pointclouds in the folder 'data'

    Args:
        folder (str): 'data' directory who contains severals pointclouds (tile)
        filetype (str): pointcloud's type in folder 'data : LAS or LAZ ?

    Returns:
        li(List): List of pointclouds (name)
    """
    li = []
    f = os.listdir(folder)
    for e in f:
        extension = e.rpartition('.')[-1]
        if extension in filetype:
            li.append(e)
    return li

def start_pool(target_folder, src, filetype = 'las', postprocess = 0,
               size = 1, method = 'startin-Laplace'):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = listPointclouds(target_folder, filetype)
    cores = cpu_count()
    print(f"Found {cores} logical cores in this PC")
    num_threads = cores -1
    if CPU_LIMIT > 0 and num_threads > CPU_LIMIT:
        print(f"Limit CPU usage to {CPU_LIMIT} cores due to env var CPU_LIMIT")
        num_threads = CPU_LIMIT
    print("\nStarting interpolation pool of processes on the {}".format(
        num_threads) + " logical cores.\n")

    if len(fnames) == 0:
        print("Error: No file names were input. Returning."); return
    pre_map, processno = [], len(fnames)
    for i in range(processno):
        pre_map.append([src, int(postprocess), float(size),
                            target_folder, fnames[i].strip('\n'), method, filetype])
    p = Pool(cores -1)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
