# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# Merge the severals LIDAR tiles around the tile and raster preparation

from commons import commons
import os
import re
import math
import numpy as np
import pdal
import laspy
import json
from tasks.las_clip import las_crop


def create_files(_file: str):
    """Create the name arround LIDAR tile

    Args:
        _file(str): name of LIDAR file (do not provide the full path)
    Returns:
        _Listinput(list): List of LIDAR's name
    """
    # Listinput = from_list(_file)
    elements = _file.split("_", 4)
    # Create name of LIDAR tiles who cercle the tile
    # # Parameters
    _prefix = f"{elements[0]}_{elements[1]}"
    _suffix = elements[-1]
    coord_x = int(elements[2])
    coord_y = int(elements[3])
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

# def from_list(_file: list):
#     """ Extract list from LIDAR name

#     Args:
#         _file(str): name of LIDAR

#     Returns:
#         _Listparser(list): List of parser
#     """
#     # Regex
#     pattern = r'(?x)^(?P<type>[a-zA-Z]+)_(?P<date>[1-2][0-9]{3})_(?P<coord_x>[0-9]{4})_(?P<coord_y>[0-9]{4})_(?P<p_proj>[A-Z0-9]+)_(?P<v_proj>[A-Z0-9]+)(_[0-9]*)?\.(?P<ext>[a-zA-Z0-9]{0,3})$'
#     # list of parser
#     _parser = re.split(pattern, _file)
#     _Listparser = list(filter(None, _parser))
#     return _Listparser

def check_name(_coord):
    """Add '0' if the coordinate X or Y who strats by '0'

    Args:
        _coord(str): the coordinate X or Y

    Returns:
        new_x(str): the new coordinate X or Y

    """
    # If the number start by "0..."
    if len(_coord) == 3:
        new_coordinate = f"0{_coord}"
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

def check_tile_ground_exist(list_las: list):
    """ Check if grounds pointcloud exist
    Args:
        list_las (list): Regex who contains the list of tiles arround the LIDAR tile

    Returns:
        li(List): Return a new list of ground's pointcloud : check if files exist or not exist
    """
    li = []
    for i in list_las:
        if not os.path.exists(i):
            print('NOK :', i)
            pass
        else:
            li.append(i)
    return li

def create_liste(las_dir, input_file):
    """Return the list of 8 tiles around the LIDAR
    Args:
        las_dir (str): directory of pointclouds
        input_file (str): path to queried LIDAR tile

    Returns:
        Listfiles(li): list of tiles
    """
    # Parameters
    # root = os.path.splitext(fname)[0]
    # Fileoutput = os.path.join(input_dir, f"{root}_ground.las")

    # Return list 8 tiles around the tile
    Listinput = create_files(os.path.basename(input_file))
    # List of pointcloud
    li = [os.path.join(las_dir, e) for e in Listinput]
    # Check the list
    li = check_tile_ground_exist(li)
    # Appending queried tile to list
    li.append(input_file)

    return li

def las_merge(las_dir, input_file, merge_file):
    """Merge LIDAR tiles around input_file tile
    Args:
        las_dir (str): directory of pointclouds (to look for neigboprs)
        input_file (str): name of query LIDAR file (with extension)
        output_file (str): path to output
    """
    # List files to merge
    Listfiles = create_liste(las_dir, input_file)
    if len(Listfiles) > 0:
        # Merge
        information = {}
        information = {
                "pipeline":
                        Listfiles + [merge_file]
        }
        merge = json.dumps(information, sort_keys=True, indent=4)
        print(merge)
        pipeline = pdal.Pipeline(merge)
        pipeline.execute()
    else:
        print('List of tiles is not okay : stop the traitment')


def create_las_with_buffer(input_dir: str, tile_filename: str,
                           merge_filename: str, crop_filename: str,
                           buffer_width=100):
    """Merge lidar tiles around the queried tile and crop them in order to add a buffer
    to the tile (usually 100m)
    Args:
        input_dir (str): directory of pointclouds (where you look for neigbors)
        tile_filename (str): full path to the queried LIDAR tile
        merge_filename (str): full path to the saved merged tile
        crop_filename (str) : full path to the saved cropped tile
        size (int): raster cell size
        buffer_width (int): width of the border to add to the tile (in pixels)
    """
    # STEP 1: Merge LIDAR tiles
    las_merge(input_dir, tile_filename, merge_filename)

    # STEP 2 : Crop filter removes points that fall inside a cropping bounding box (2D) (with buffer 100 m)
    bounds = commons.las_info(tile_filename, buffer_width=buffer_width)
    las_crop(merge_filename, crop_filename, bounds)


def read_las_file_to_numpy(input_file, size):
    """Takes the filepath to an input LAS (crop) file and the desired output raster cell size
    Reads the LAS file and outputs the ground points as a numpy array.
    Also establishes some asic raster parameters:
    - the extents
    - the resolution in coordinates
    - the coordinate location of the relative origin (bottom left)
        """
    in_file = laspy.read(input_file)
    header = in_file.header
    in_np = np.vstack((in_file.raw_classification,
                           in_file.x, in_file.y, in_file.z)).transpose()
    in_np = in_np[in_np[:,0] == 2].copy()[:,1:]
    extents = [[header.min[0], header.max[0]],
               [header.min[1], header.max[1]]]
    res = [math.ceil((extents[0][1] - extents[0][0]) / size),
           math.ceil((extents[1][1] - extents[1][0]) / size)]
    origin = [np.mean(extents[0]) - (size / 2) * res[0],
              np.mean(extents[1]) - (size / 2) * res[1]]
    return in_np, res, origin


def las_prepare(input_dir: str, output_dir: str, temp_dir: str, fname: str, size: float):
    """Severals steps :
        1- Create tile with buffer
        2- Read the new tile and establish basic raster parameter (ct read_las_file_to_numpy)

    Args:
        input_dir (str): directory of pointclouds
        output_dir (str): directory folder for saving the outputs
        fname (str): name of LIDAR tile
        size (int): raster cell size

    Returns:
        extents(array) : extents
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
    """
    # Parameters
    tile_name = os.path.splitext(fname)[0]
    ground_file = os.path.join(output_dir, f"{tile_name}_ground.las")
    merge_file = os.path.join(temp_dir, f'{tile_name}_merge.las')
    crop_file = os.path.join(temp_dir, f"{tile_name}_crop.las")

    create_las_with_buffer(output_dir, ground_file, merge_file, crop_file, buffer_width=100)
    in_np, res, origin = read_las_file_to_numpy(crop_file, size)

    return in_np, res, origin