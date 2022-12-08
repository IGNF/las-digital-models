# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# MAIN FILE FOR PRE-PROCESSING  


"""Key to CMD arguments:
    1:  target folder (most likely the same as the one you used with PDAL)
        [compulsory, no default value] (folder "data")
    2:  Directory folder for saving the outputs
    3:  extension (LAS / LAZ) [default : LAS]

Output file will be written to the target folder "output" : combines input from ground pointcloud into a single output.
"""
import os
from sys import argv
from gf_processing import start_pool

def create_folder(dest_folder: str):
    """Create the severals folders "DTM" and "_tmp" if not exist"""
    # Create folder "DTM"
    DTM_new_dir = os.path.join(dest_folder, 'DTM')
    if not os.path.isdir(DTM_new_dir):
        os.makedirs(DTM_new_dir)
    # Create folder "_tmp"
    tmp_new_dir = os.path.join(dest_folder, '_tmp')
    if not os.path.isdir(tmp_new_dir):
        os.makedirs(tmp_new_dir)

def main():    
    # Create the severals folder if not exists
    create_folder(argv[2])
    if len(argv) <= 4: start_pool(*argv[1:])
    else: print("Error: Incorrect number of arguments passed. Returning.")
    
if __name__ == '__main__':
    main()