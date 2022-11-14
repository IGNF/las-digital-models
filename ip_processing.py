# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# INTERPOLATION + POST-PROCESSING SCRIPTS 

import os
from time import time
from multiprocessing import Pool, cpu_count
import numpy as np
from las_prepare import las_prepare


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
        _size = str('')

    return _size

def execute_startin(pts, res, origin, size, method):
    """Takes the grid parameters and the ground points. Interpolates
    either using the TIN-linear or the Laplace method. Uses a
    -9999 no-data value. 
    Fully based on the startin package (https://startinpy.readthedocs.io/en/latest/api.html)
    Args:
        pts : ground points
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
        size (int): raster cell size
        method(str): spatial interpolation, deterministic metho (TIN or Laplace)
    
    Returns:
        ras(list): Z interpolation
    """
    import startinpy
    import numpy as np

    # # Startin 
    tin = startinpy.DT(); tin.insert(pts) # # Insert each points in the array of points (a 2D array)
    ras = np.zeros([res[1], res[0]]) # # returns a new array of given shape and type, filled with zeros
    # # Interpolate method
    if method == 'startin-TINlinear':
        def interpolant(x, y): return tin.interpolate_tin_linear(x, y)
    elif method == 'startin-Laplace':
        def interpolant(x, y): return tin.interpolate_laplace(x, y)
    else:
        print('error')
    yi = 0
    for y in np.arange(origin[1], origin[1] + res[1] * size, size):
        xi = 0
        for x in np.arange(origin[0], origin[0] + res[0] * size, size):
            ch = tin.is_inside_convex_hull(x, y) # check is the point [x, y] located inside  the convex hull of the DT
            if ch == False:
                ras[yi, xi] = -9999 # no-data value
            else:
                tri = tin.locate(x, y) # locate the triangle containing the point [x,y]. An error is thrown if it is outside the convex hull
                if tri != [] and 0 not in tri:
                    ras[yi, xi] = interpolant(x, y)
                else: ras[yi, xi] = -9999 # no-data value
            xi += 1
        yi += 1
    return ras

def execute_cgal(pts, res, origin, size):
    """Performs CGAL-NN on the input points.
    First it removes any potential duplicates from the
    input points, as these would cause issues with the
    dictionary-based attribute mapping.
    Then, it creates CGAL Point_2 object from these points,
    inserts them into a CGAL Delaunay_triangulation_2, and
    performs interpolation using CGAL natural_neighbor_coordinate_2
    by finding the attributes (Z coordinates) via the dictionary
    that was created from the deduplicated points.
    Args:
        pts : ground points
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
        size (int): raster cell size
    
    Returns:
        ras(list): Z interpolation
    """
    from CGAL.CGAL_Kernel import Point_2
    from CGAL.CGAL_Triangulation_2 import Delaunay_triangulation_2
    from CGAL.CGAL_Interpolation import natural_neighbor_coordinates_2

    s_idx = np.lexsort(pts.T); s_data = pts[s_idx,:]
    mask = np.append([True], np.any(np.diff(s_data[:,:2], axis = 0), 1))
    deduped = s_data[mask]
    cpts = list(map(lambda x: Point_2(*x), deduped[:,:2].tolist()))
    zs = dict(zip([tuple(x) for x in deduped[:,:2]], deduped[:,2]))

    tin = Delaunay_triangulation_2()
    for pt in cpts: tin.insert(pt)
    ras = np.zeros([res[1], res[0]])
    yi = 0
    for y in np.arange(origin[1], origin[1] + res[1] * size, size):
        xi = 0
        for x in np.arange(origin[0], origin[0] + res[0] * size, size):
            nbrs = [];
            qry = natural_neighbor_coordinates_2(tin, Point_2(x, y), nbrs)
            if qry[1] == True:
                z_out = 0
                for nbr in nbrs:
                    z, w = zs[(nbr[0].x(), nbr[0].y())], nbr[1] / qry[0]
                    z_out += z * w
                ras[yi, xi] = z_out
            else: ras[yi, xi] = -9999
            xi += 1
        yi += 1
    return ras

def execute_pdal(fpath, size, rad, pwr, wnd):
    """Sets up a PDAL pipeline that reads a ground filtered LAS
    file, and writes it via GDAL. The GDAL writer has interpolation
    options, exposing the radius, power and a fallback kernel width
    to be configured. More about these in the readme on GitHub.
    Args:
        fpath(str): target folder 
        size (float): raster cell size
        rad(float): radius [default:5]
        pwr(float): exponent of distance when computing IDW. CLose points have higher significance than far points. [default:2]
        wnd(float): the maximum distance from donor cell to a target cell when applying the fallback interpolation method. [default:0]
    """
    import pdal
    import json

    # # Return size for output's name
    _size = give_name_resolution_raster(size)

    Fileoutput = "_".join([fpath[:-4], "_".join([_size,'IDW.tif'])])
    information = {}
    information = {
        "pipeline": [
            {
                "type":"readers.las",
                "filename":fpath,
                "override_srs": "EPSG:2154",
                "nosrs": True
            },
            {
                "type":"filters.range",
                "limits":"Classification[2:2]"
            },
            {
                "output_type": "idw",
                "resolution": str(size),
                "radius": str(rad),
                "power": str(pwr),
                "window_size": str(wnd),    
                "data_type": "float32",
                "filename": Fileoutput
            }
        ]
    }
    # # "NOSRS" = Don’t read the SRS VLRs. The data will not be assigned an SRS. 
    # # This option is for use only in special cases where processing the SRS could cause performance issues. [Default: false]
    ground = json.dumps(information, sort_keys=True, indent=4)
    pipeline = pdal.Pipeline(ground)
    pipeline.execute()

def execute_idwquad(pts, res, origin, size,
                    start_rk, pwr, minp, incr_rk, method, tolerance, maxiter):
    """Creates a KD-tree representation of the tile's points and
    executes a quadrant-based IDW algorithm on them. Although the
    KD-tree is based on a C implementation, the rest is coded in
    pure Python (below). Keep in mind that because of this, this
    is inevitably slower than the rest of the algorithms here.
    To optimise performance, one is advised to fine-tune the
    parametrisation, especially tolerance and maxiter.
    More info in the GitHub readme.
    """
    from scipy.spatial import cKDTree
    ras = np.zeros([res[1], res[0]])
    tree = cKDTree(np.array([pts[:,0], pts[:,1]]).transpose())
    yi = 0
    for y in np.arange(origin[1], origin[1] + res[1] * size, size):
        xi = 0
        for x in np.arange(origin[0], origin[0] + res[0] * size, size):
            done, i, rk = False, 0, start_rk
            while done == False:
                if method == "radial":
                    ix = tree.query_ball_point([x, y], rk, tolerance)
                elif method == "k-nearest":
                    ix = tree.query([x, y], rk, tolerance)[1]
                xyp = pts[ix]
                qs = [
                        xyp[(xyp[:,0] < x) & (xyp[:,1] < y)],
                        xyp[(xyp[:,0] > x) & (xyp[:,1] < y)],
                        xyp[(xyp[:,0] < x) & (xyp[:,1] > y)],
                        xyp[(xyp[:,0] > x) & (xyp[:,1] > y)]
                     ]
                if min(qs[0].size, qs[1].size,
                       qs[2].size, qs[3].size) >= minp: done = True
                elif i == maxiter:
                    ras[yi, xi] = -9999; break
                rk += incr_rk; i += 1
            else:
                asum, bsum = 0, 0
                for pt in xyp:
                    dst = np.sqrt((x - pt[0])**2 + (y - pt[1])**2)
                    u, w = pt[2], 1 / dst ** pwr
                    asum += u * w; bsum += w
                    ras[yi, xi] = asum / bsum
            xi += 1
        yi += 1
    return ras

def write_geotiff(raster, origin, size, fpath):
    """Writes the interpolated TIN-linear and Laplace rasters
    to disk using the GeoTIFF format. The header is based on
    the raster array and a manual definition of the coordinate
    system and an identity affine transform.
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
            print(fpath)

def patch(raster, res, origin, size, min_n):
    """Patches in missing pixel values by applying a median
    kernel (3x3) to estimate its value. This is meant to serve
    as a means of populating missing pixels, not as a means
    of interpolating large areas. The last parameter should
    be an integer that specifies the minimum number of valid
    neighbour values to fill a pixel (0 <= min_n <= 8).
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
    src, target_folder, postprocess = mp[0], mp[3], mp[1]
    size, fpath = mp[2], ("DTM/".join([mp[0], mp[4][:-4]]))
    fname, method = mp[4], mp[5]
    idw0_polyfpath, idw1, idw2, idw3 = mp[6], mp[7], mp[8], mp[9] 
    idw4, idw5, idw6 = mp[10], mp[11], mp[12]
    print("PID {} starting to work on {}".format(os.getpid(), fname))
    start = time()
    gnd_coords, res, origin = las_prepare(target_folder, src, fname, size)
    if method == 'PDAL-IDW':
        execute_pdal("".join([target_folder, mp[4]]), size,
                     idw0_polyfpath, idw1, idw2)
        end = time()
        print("PID {} finished interpolation and export.".format(os.getpid()),
          "Time elapsed: {} sec.".format(round(end - start, 2)))
        return
    if method == 'startin-TINlinear' or method == 'startin-Laplace':
        ras = execute_startin(gnd_coords, res, origin, size, method)
    elif method == 'CGAL-NN':
        ras = execute_cgal(gnd_coords, res, origin, size)
    elif method == 'IDWquad':
        ras = execute_idwquad(gnd_coords, res, origin, size,
                              idw0_polyfpath, idw1, idw2, idw3,
                              idw4, idw5, idw6)
    end = time()
    print("PID {} finished interpolating.".format(os.getpid()),
          "Time spent interpolating: {} sec.".format(round(end - start, 2)))
    if postprocess > 0:
        start = time
        print("PID {} finished post-processing.".format(os.getpid()),
              "Time spent post-processing: {} sec.".format(
                  round(end - start, 2)))
    # Return size for output's name
    _size = give_name_resolution_raster(size)
    # Write raster
    start = time()
    if method == 'startin-TINlinear':
        write_geotiff(ras, origin, size, fpath + _size + '_TINlinear.tif')
    if method == 'startin-Laplace':
        write_geotiff(ras, origin, size, fpath + _size + '_Laplace.tif')
    if method == 'CGAL-NN':
        write_geotiff(ras, origin, size, fpath + _size + '_NN.tif')
    if method == 'IDWquad':
        write_geotiff(ras, origin, size, fpath + _size + '_IDWquad.tif')
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
        if "ground" in e:
            pass
        else:
            extension = e.rpartition('.')[-1]
            if extension in filetype:
                li.append(e)
    return li

def start_pool(target_folder, src, filetype = 'las', postprocess = 0,
               size = 1, method = 'startin-Laplace', idw0_polyfpath = 5, 
               idw1 = 2, idw2 = 0, idw3 = 2,
               idw4 = 'radial', idw5 = 0.2, idw6 = 3):
    """Assembles and executes the multiprocessing pool.
    The interpolation variants/export formats are handled
    by the worker function (ip_worker(mapped)).
    """
    fnames = listPointclouds(target_folder, filetype)
    cores = cpu_count()
    print("\nStarting interpolation pool of processes on the {}".format(
        cores) + " logical cores found in this PC.\n")
    if cores < len(fnames):
        print("Warning: more processes in pool than processor cores.\n" +
              "Optimally, roughly as many processes as processor " +
              "cores should be run concurrently.\nYou are starting " +
              str(len(fnames)) + " processes on " + str(cores) + " cores.\n")
    elif len(fnames) == 0:
        print("Error: No file names were input. Returning."); return
    pre_map, processno = [], len(fnames)
    for i in range(processno):
        pre_map.append([src, int(postprocess), float(size),
                            target_folder, fnames[i].strip('\n'), method,
                            idw0_polyfpath, float(idw1), float(idw2),
                            float(idw3), idw4, float(idw5), float(idw6), filetype])
    p = Pool(processes = processno)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
