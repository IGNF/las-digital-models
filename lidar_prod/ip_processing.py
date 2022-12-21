# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# INTERPOLATION + POST-PROCESSING SCRIPTS USING MULTIPROCESSING

from commons import commons
import os
from time import time
from multiprocessing import Pool, cpu_count
from tasks.las_prepare import las_prepare
from tasks.las_interpolation_deterministic import deterministic_method
from tasks.las_raster_generation import export_raster


CPU_LIMIT=int(os.getenv("CPU_LIMIT", "-1"))


def ip_worker(mp):
    """Multiprocessing worker function to be used by the
    p.map function to map objects to, and then start
    multiple times in parallel on separate CPU cores.
    In this case the worker function instances interpolate
    one file each, writing the resulting rasters to disk.
    Runs slightly different workflows depending on the
    desired interpolation method/export format.
    Args:
        mp: list of arguments: eg [output_dir, int(postprocess), float(size),
                            target_folder, fnames[i], method, filetype]
    """
    # Parameters
    output_dir = mp[0]
    temp_dir = mp[1]
    postprocess = mp[2]
    size = mp[3]
    input_dir = mp[4]
    fname = mp[5]
    method =  mp[6]
    tile_name = os.path.splitext(fname)[0]

    # Generate output filenames
    # Las preparation
    ground_file = os.path.join(output_dir, f"{tile_name}_ground.las")
    merge_file = os.path.join(temp_dir, f'{tile_name}_merge.las')
    crop_file = os.path.join(temp_dir, f"{tile_name}_crop.las")

    # raster export
    _size = commons.give_name_resolution_raster(size)
    geotiff_filename = f"{tile_name}{_size}_{commons.method_postfix[method]}.tif"
    geotiff_path_temp = os.path.join(temp_dir, geotiff_filename)
    geotiff_path = os.path.join(output_dir, geotiff_filename)

    # Extract coordinate, resolution and coordinate location of the relative origin
    print("PID {} starting to work on {}".format(os.getpid(), fname))
    start = time()
    gnd_coords, res, origin = las_prepare(output_dir, ground_file, merge_file, crop_file, size)
    # Interpolation with method deterministic
    _interpolation = deterministic_method(gnd_coords, res, origin, size, method)

    ras = _interpolation.run(pdal_idw_input=crop_file, pdal_idw_output=geotiff_path_temp)
    end = time()
    print("PID {} finished interpolating.".format(os.getpid()),
          "Time spent interpolating: {} sec.".format(round(end - start, 2)))
    # if postprocess > 0:
    #     start = time
    #     print("PID {} finished post-processing.".format(os.getpid()),
    #           "Time spent post-processing: {} sec.".format(
    #               round(end - start, 2)))

    # Write raster in the folder DTM who clipping from the LIDAR tile
    start = time()
    export_raster(os.path.join(input_dir, fname), ras, origin, size, geotiff_path_temp,
        geotiff_path, method)
    end = time()
    print("PID {} finished exporting.".format(os.getpid()),
          "Time spent exporting: {} sec.".format(round(end - start, 2)))


def start_pool(input_dir, output_dir, temp_dir='/tmp', filetype = 'las', postprocess = 0,
               size = 1, method = 'startin-Laplace'):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = commons.listPointclouds(input_dir, filetype)
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
        pre_map.append([output_dir, temp_dir, int(postprocess), float(size),
                            input_dir, fnames[i], method, filetype])
    p = Pool(cores -1)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
