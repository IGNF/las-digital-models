# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# PRE-PROCESSING

import os
from time import time
import re
import shutil
from multiprocessing import Pool, cpu_count
import numpy as np
from las_prepare import las_prepare
from las_merge import las_merge


def create_files(_file):
    """Create the name arround LIDAR tile

    Args:
        _file(str): name of LIDAR

    Returns:
        _Listinput(list): List of LIDAR's name
    """
    Listinput = from_list(_file)
    # # Create name of LIDAR tiles who cercle the tile
    # # Parameters
    _prefix = str("_".join([Listinput[0], Listinput[1]]))
    _suffix = str("_".join([Listinput[4], ".".join([Listinput[5], Listinput[6]])]))
    coord_x = int(Listinput[2])
    coord_y = int(Listinput[3])
    # # Create coordinate arround the LIDAR tile
    _result = create_coordinate(coord_x, coord_y)
    # # Coordinate X or Y - 1
    coord_less_x = str(_result[0])
    coord_less_y = str(_result[1])
    # # Coordinate X or Y + 1
    coord_more_x = str(_result[2])
    coord_more_y = str(_result[3])
    # On left
    _tile_hl = str(_prefix + '_' + coord_less_x + '_' + coord_more_y + '_' + _suffix)
    _tile_ml = str(_prefix + '_' + coord_less_x + '_' + check_name(str(coord_y)) + '_' + _suffix)
    _tile_bl = str(_prefix + '_' + coord_less_x + '_' + coord_less_y + '_' + _suffix)
    # On Right 
    _tile_hr = str(_prefix + '_' + coord_more_x + '_' + coord_more_y + '_' + _suffix)
    _tile_mr = str(_prefix + '_' + coord_more_x + '_' + check_name(str(coord_y)) + '_' + _suffix)
    _tile_br = str(_prefix + '_' + coord_more_x + '_' + coord_less_y + '_' + _suffix)
    # Above
    _tile_a = str(_prefix + '_' + check_name(str(coord_x)) + '_' + coord_more_y + '_' + _suffix)
    # Below
    _tile_b = str(_prefix + '_' + check_name(str(coord_x)) + '_' + coord_less_y + '_' + _suffix)
    # Return the severals tile's names
    return _tile_hl, _tile_ml, _tile_bl, _tile_a, _tile_b, _tile_hr, _tile_mr, _tile_br

def from_list(_file):
    """ Extract list from LIDAR name

    Args:
        _file(str): name of LIDAR

    Returns:
        _Listparser(list): List of parser
    """
    # Regex
    pattern = r'(?x)^(?P<type>[a-zA-Z]+)_(?P<date>[1-2][0-9]{3})_(?P<coord_x>[0-9]{4})_(?P<coord_y>[0-9]{4})_(?P<p_proj>[A-Z0-9]+)_(?P<v_proj>[A-Z0-9]+)(_[0-9]*)?\.(?P<ext>[a-zA-Z0-9]{0,3})$'
    # list of parser
    _parser = re.split(pattern, _file)
    _Listparser = list(filter(None, _parser))
    return _Listparser

def check_name(_coord):
    """Add '0' if the coordinate X or Y who strats by '0' 

    Args:
        _coord(str): the coordinate X or Y

    Returns:
        new_x(str): the new coordinate X or Y
    
    """
    # If the number start by "0..."
    if len(_coord) == 3:
        new_coordinate = ''.join(['0', _coord])
    else:
        new_coordinate = _coord
    return new_coordinate

def create_coordinate(_x, _y):
    """Create coordinate arround the LIDAR tile

    Args:
        _x(str): the coordinate X
        _y(str): the coordinate Y

    Returns:
        coord_less_x(str): the new coordinate X - 1
        coord_less_y(str): the new coordinate Y - 1
        coord_more_x(str): the new coordinate X + 1
        coord_more_y(str): the new coordinate Y + 1
    
    """
    # Coordinate X or Y - 1
    coord_less_x = check_name(str(_x - 1))
    coord_less_y = check_name(str(_y - 1))
    # Coordinate X or Y + 1
    coord_more_x = check_name(str(_x + 1))
    coord_more_y = check_name(str(_y + 1))
    return coord_less_x, coord_less_y, coord_more_x, coord_more_y

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

def ip_worker(mp):
    """Multiprocessing worker function to be used by the
    p.map function to map objects to, and then start
    multiple times in parallel on separate CPU cores.
    In this case the worker function instances prepare
    one file each, writing the resulting merge LIDAR.
    """
    fpath = (mp[0] + mp[1])[:-3] + mp[2]
    fname = mp[1]
    dst = str("_tmp".join([fpath[:-5], '/']))
    # Create folder "_tmp"
    if os.path.isdir('./_tmp') is False:
        os.makedirs('_tmp')
    # Regex
    Listinput = create_files(fname)
    # List of pointcloud
    li = []
    output = str(fname.join([dst, '_merge.las']))
    f = Listinput # List of 8 tiles arond the data
    for e in f:
        if "_merge" in e:
            pass
        else:
            e = "".join([fpath, e])
            li.append(e)
    # Appending output to list
    li.extend([output])
    start = time()
    las_merge(fpath, li)
    end = time()
    # print("PID {} finished merge.".format(os.getpid()),
    #       "Time spent merging: {} sec.".format(round(end - start, 2)))
    # print("PID {} starting to work on {}".format(os.getpid(), fname))
    # start = time()
    # las_prepare(fpath)
    # end = time()
    # print("PID {} finished classify.".format(os.getpid()),
    #       "Time spent classifing: {} sec.".format(round(end - start, 2)))

def start_pool(target_folder, filetype = 'las'):
    """Assembles and executes the multiprocessing pool.
    The pre-processing are handled
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
        pre_map.append([target_folder, fnames[i].strip('\n'), filetype])
    p = Pool(processes = processno)
    p.map(ip_worker, pre_map)
    p.close(); p.join()
    print("\nAll workers have returned.")
